import cohere
import chromadb
import time

# ---------------------- 1. DIVISIÓN DEL TEXTO EN CHUNKS ----------------------
from langchain.text_splitter import RecursiveCharacterTextSplitter

def dividir_en_chunks(txt_path, chunk_size=2000, overlap=300):
    """
    Divide el texto en chunks utilizando LangChain's RecursiveCharacterTextSplitter.
    :param txt_path: Ruta del archivo de texto.
    :param chunk_size: Tamaño máximo de cada chunk en caracteres.
    :param overlap: Cantidad de caracteres que se solapan entre chunks.
    :return: Una lista de chunks de texto.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        texto = f.read()

    # Configurar el divisor de texto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    
    # Dividir el texto en chunks
    chunks = text_splitter.split_text(texto)
    print(f"Texto dividido en {len(chunks)} chunks de tamaño máximo {chunk_size} con solapamiento {overlap}.")
    return chunks




# ---------------------- 2. GENERACIÓN DE EMBEDDINGS ----------------------
cohere_client = cohere.Client("COHERE_API_KEY")  

import time

def obtener_embeddings(chunks):
    """
    Obtiene los embeddings usando la API de Cohere, procesando por lotes.
    """
    embeddings = []
    batch_size = 2  # Número de chunks por lote, ajustable

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"Obteniendo embeddings para el batch {i // batch_size + 1}...")
        try:
            response = cohere_client.embed(texts=batch)
            embeddings.extend(response.embeddings)
        except Exception as e:
            print(f"Error al obtener embeddings: {e}")
            time.sleep(10)  # Esperar si hay un error, luego reintentar
            continue
        
        time.sleep(1)  # Pausa entre lotes para evitar el límite por minuto

    print("Embeddings generados correctamente.")
    return embeddings

# ---------------------- 3. ALMACENAMIENTO EN CHROMADB HACIENDO LA BD PERSISTENTE ----------------------
import chromadb
import shutil
import os

# Ruta de la base de datos persistente
PERSISTENT_DB_PATH = "./data/chromadb"

# Inicializa el cliente de Chromadb con persistencia
client = chromadb.PersistentClient(path=PERSISTENT_DB_PATH)
print("Base de datos persistente inicializada correctamente.")

def almacenar_embeddings(embeddings, chunks, collection_name="documentos"):
    """
    Almacena los embeddings y los textos correspondientes en la base de datos de Chromadb.
    :param embeddings: Lista de embeddings generados.
    :param chunks: Lista de fragmentos de texto.
    :param collection_name: Nombre de la colección en Chromadb.
    """
    # Intentar obtener la colección existente o crear una nueva
    try:
        # Intentar obtener la colección si ya existe
        collection = client.get_collection(name=collection_name)
        print(f"Se ha cargado la colección '{collection_name}'.")
    except Exception as e:
        # Si la colección no existe, se crea una nueva
        print(f"Creando nueva colección: {e}")
        collection = client.create_collection(
            name=collection_name,
            metadata={"dimensionality": 384}  # La dimensión de los embeddings, en este caso, 384
        )

    # Insertar los embeddings en la colección
    for idx, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
        collection.add(
            ids=[f"doc_{idx}"],  # ID único para cada fragmento
            metadatas=[{"id": str(idx)}],  # Metadata del fragmento
            documents=[chunk],  # El fragmento de texto
            embeddings=[embedding]  # El embedding correspondiente
        )
    print("Embeddings almacenados correctamente.")



# Funcion completa que integra todas las demás funciones
def procesar_y_guardar_embeddings(txt_path, chunk_size=2000, overlap=300):
    """
    Procesa el texto dividiéndolo en chunks grandes con solapamiento y guarda sus embeddings.
    :param txt_path: Ruta del archivo de texto.
    :param chunk_size: Tamaño de los chunks en caracteres.
    :param overlap: Cantidad de caracteres que se solapan entre chunks.
    """
    # Dividir el texto en chunks grandes con solapamiento
    chunks = dividir_en_chunks(txt_path, chunk_size=chunk_size, overlap=overlap)

    # Generar embeddings para los chunks
    embeddings = obtener_embeddings(chunks)

    # Guardar los embeddings en Chromadb
    almacenar_embeddings(embeddings, chunks)




# ---- PRUEBAS ---

# ---------------------- 4. PRUEBAS DE BÚSQUEDA EN CHROMADB ----------------------
def buscar_en_chromadb(query, collection_name="documentos"):
    """
    Realiza una búsqueda en la base de datos de ChromaDB utilizando una consulta.
    :param query: Consulta en lenguaje natural.
    :param collection_name: Nombre de la colección en ChromaDB.
    """
    try:
        collection = client.get_collection(name=collection_name)
        response = cohere_client.embed(texts=[query])
        query_embedding = response.embeddings[0]
        
        resultados = collection.query(
            query_embeddings=[query_embedding],
            n_results=5  # Número de resultados más relevantes
        )
        
        print("Resultados de la búsqueda:")
        for i, documento in enumerate(resultados["documents"][0]):
            print(f"Resultado {i + 1}: {documento}")
    except Exception as e:
        print(f"Error durante la búsqueda: {e}")