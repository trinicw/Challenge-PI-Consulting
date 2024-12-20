# app/routers/consulta.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.buscar import buscar_y_generar_respuesta  # Importar la función desde buscar.py
import cohere

# Inicializa el cliente de Cohere
cohere_client = cohere.Client("COHERE_API_KEY")

# Modelo Pydantic para recibir la consulta del usuario
class ConsultaRequest(BaseModel):
    query: str

# Crear el router de FastAPI
router = APIRouter()

# Endpoint POST para procesar la consulta
@router.post("/consulta")
async def consulta(request: ConsultaRequest):
    """
    Genera el embedding de la query, envía el embedding a buscar.py
    y devuelve la respuesta generada al frontend.
    """
    try:
        query = request.query  # Extraer la consulta desde el request

        # Generar el embedding de la query usando Cohere
        response = cohere_client.embed(texts=[query])
        query_embedding = response.embeddings[0]

        # Pasar el embedding y la query a buscar.py para obtener la respuesta final
        respuesta_llm = buscar_y_generar_respuesta(query_embedding, query)

        # Enviar la respuesta generada al frontend
        return {"respuesta": respuesta_llm}

    except Exception as e:
        # Manejo de errores
        raise HTTPException(status_code=500, detail=str(e))
