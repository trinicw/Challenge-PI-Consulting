from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
import json
from uuid import uuid4
import numpy as np
from dotenv import load_dotenv
import os
import cohere
from langchain.text_splitter import RecursiveCharacterTextSplitter

import hashlib

# Función para generar un ID único
def generate_doc_id(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Aseguramos que la carpeta de recursos exista
os.makedirs('./resources', exist_ok=True)

# Almacenamiento en memoria
embeddings = {}
documents = {}

# Inicialización de FastAPI
app = FastAPI()

# Inicialización de Cohere
load_dotenv()
api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(api_key)

class Document(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the document")
    content: str = Field(..., min_length=1, description="Content of the document")
    
    @validator('title')
    def title_not_empty(cls, value):
        if not value.strip():
            raise ValueError("Title cannot be empty")
        return value
    
    @validator('content')
    def content_not_empty(cls, value):
        if not value.strip():
            raise ValueError("Content cannot be empty")
        return value

class GenerateEmbeddings_Request(BaseModel):
    document_id: str

class SearchRequest(BaseModel):
    query: str

class AskRequest(BaseModel):
    question: str

def cosine_similarity_manual(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def splitt(content: str):
    chunk_size = 2300
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size // 10)
    return text_splitter.split_text(content)

def save_doc(input_doc: Document, save_local=True):
    doc_id = generate_doc_id(input_doc.content)
    if doc_id in documents:
        return {
            "message": "Document already exists",
            "document_id": doc_id,
            "chunk_count": len(documents[doc_id]["chunks"])
        }
    chunks = splitt(input_doc.content)
    documents[doc_id] = {
        "title": input_doc.title,
        "chunks": []
    }
    for index, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_{index}"
        chunk_data = {
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "title": input_doc.title,
            "content": chunk
        }
        documents[doc_id]["chunks"].append(chunk_data)
        if save_local:
            with open(f"./resources/{chunk_id}.json", "w") as fp:
                json.dump(chunk_data, fp)
    return {
        "message": "Document successfully uploaded",
        "document_id": doc_id,
        "chunk_count": len(chunks)
    }

def embedd_doc(doc_id: str):
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    for chunk in documents[doc_id]["chunks"]:
        try:
            embeddings[chunk["chunk_id"]] = co.embed(
                texts=[chunk["content"]],
                model="embed-multilingual-v2.0"            
            ).embeddings[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error generating embeddings: " + str(e))
    return {"message": f"Embeddings generated successfully for document {doc_id}"}

def load_documents():
    global documents
    documents = {}
    for filename in os.listdir('./resources'):
        if filename.endswith('.json'):
            with open(f'./resources/{filename}', 'r') as fp:
                chunk_data = json.load(fp)
                doc_id = chunk_data["doc_id"]
                if doc_id not in documents:
                    documents[doc_id] = {
                        "title": chunk_data["title"],
                        "chunks": []
                    }
                documents[doc_id]["chunks"].append(chunk_data)

@app.get("/list_documents")
async def list_docs():
    return list(documents.values())

@app.post("/upload")
async def upload_doc(doc: Document):
    return save_doc(doc)

@app.post("/generate_embeddings")
async def embedd_document(request: GenerateEmbeddings_Request):
    return embedd_doc(request.document_id)

@app.post("/search")
async def search(request: SearchRequest):
    query = request.query
    query_embedding = co.embed(
        texts=[query],
        model="embed-multilingual-v2.0"
    ).embeddings[0]
    
    results = []
    for doc_id, doc_data in documents.items():
        for chunk in doc_data["chunks"]:
            chunk_embedding = embeddings.get(chunk["chunk_id"])
            if chunk_embedding is not None:
                similarity = cosine_similarity_manual(query_embedding, chunk_embedding)
                content_snippet = chunk["content"][:150]  # Primeros 150 caracteres del contenido
                results.append({
                    "document_id": doc_id,
                    "title": chunk["title"],
                    "content_snippet": content_snippet,
                    "similarity_score": similarity
                })
    
    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
    
    return {"results": results[:5]}  

@app.post("/ask")
async def ask(request: AskRequest):
    question = request.question
    question_embedding = co.embed(
        texts=[question],
        model="embed-multilingual-v2.0"
    ).embeddings[0]
    
    relevant_chunks = []
    for doc_id, doc_data in documents.items():
        for chunk in doc_data["chunks"]:
            chunk_embedding = embeddings.get(chunk["chunk_id"])
            if chunk_embedding is not None:
                similarity = cosine_similarity_manual(question_embedding, chunk_embedding)
                if similarity > 0.2:
                    relevant_chunks.append({
                        "title": chunk["title"],
                        "content": chunk["content"],
                        "similarity_score": similarity
                    })
    
    if not relevant_chunks:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    
    context = "\n".join([f"Title: {chunk['title']}\nContent: {chunk['content']}" for chunk in relevant_chunks])
    
    try:
        answer = co.generate(
            model="command-xlarge",
            prompt=f"Answer the following question based on the provided documents:\n\nQuestion: {question}\n\nContext:\n{context}\n\nAnswer:",
            max_tokens=100
        ).generations[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating response from Cohere: " + str(e))

    return {
        "question": question,
        "answer": answer
    }
