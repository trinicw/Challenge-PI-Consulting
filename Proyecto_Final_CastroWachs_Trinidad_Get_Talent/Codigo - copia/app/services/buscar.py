# app/services/buscar.py

import chromadb
from app.services.generacion import generar_respuesta

# Inicializamos el cliente de Chromadb con persistencia
PERSISTENT_DB_PATH = "./data/chromadb"
client = chromadb.PersistentClient(path=PERSISTENT_DB_PATH)

def buscar_y_generar_respuesta(query_embedding, query, collection_name="documentos"):
    """
    Busca fragmentos relevantes en la base de datos de ChromaDB usando el embedding de la query.
    Si se encuentran resultados relevantes, los pasa a generacion.py para generar la respuesta.
    Si no hay resultados, devuelve un mensaje indicando que no se encontraron resultados relevantes.
    """
    try:
        # Obtener la colección de Chromadb
        collection = client.get_collection(name=collection_name)
        
        # Realizar la búsqueda en la base de datos
        resultados = collection.query(
            query_embeddings=[query_embedding],
            n_results=10  # Limitar a los 10 resultados más relevantes
        )

        # Si no se encontraron resultados relevantes
        if not resultados["documents"] or not resultados["documents"][0]:
            print("No se encontraron resultados relevantes.")
            return "Lo siento, no pude encontrar información relevante para tu pregunta."

        # Mostrar fragmentos y scores de similitud para depurar en consola
        fragmentos_relevantes = resultados["documents"][0]  # Primeros 10 fragmentos
        scores = resultados["distances"]  # Puntuaciones de similitud
        print("Fragmentos recuperados:", fragmentos_relevantes)
        print("Scores de similitud:", scores)

        # Generar respuesta basada en los fragmentos
        respuesta_llm = generar_respuesta(fragmentos_relevantes, query)
        return respuesta_llm

    except Exception as e:
        print(f"Error al realizar la búsqueda: {e}")
        return "Hubo un problema durante la búsqueda. Intenta nuevamente."
