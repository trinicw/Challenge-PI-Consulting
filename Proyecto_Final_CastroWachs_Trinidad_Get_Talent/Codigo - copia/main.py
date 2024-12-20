

from app.utils.procesamiento import (
    procesar_y_guardar_embeddings,
    buscar_en_chromadb
)

if __name__ == "__main__":
    # Ruta del archivo de texto limpio
    txt_path = "./data/INFORMACION_LIMPIO.txt"
    
    # Proceso de división, embeddings y almacenamiento
    print("Iniciando el procesamiento y almacenamiento de embeddings...")
    overlap = 300  # Ajusta el valor del overlap según lo necesario
    procesar_y_guardar_embeddings(txt_path, chunk_size=2000, overlap=overlap)


    # Realizar una búsqueda de prueba
    query = "¿Qué es el certificado de discapacidad?"
    print("\nRealizando búsqueda en la base de datos...")
    buscar_en_chromadb(query)

from fastapi import FastAPI
from app.routers import consulta  # Importar el router desde consulta.py

app = FastAPI()

# Incluir el router de consulta.py
app.include_router(consulta.router)

@app.get("/")
def root():
    return {"message": "Sistema de consultas de leyes y derechos sobre discapacidad funcionando correctamente."}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import consulta  # Ajusta la importación según tu estructura


# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Permite solicitudes desde el frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

app.include_router(consulta.router)
