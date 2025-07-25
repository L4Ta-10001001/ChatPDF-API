# main.py

import os
import hashlib
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import fitz  # PyMuPDF

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain.callbacks import get_openai_callback
from pinecone import Pinecone, ServerlessSpec

# === Configuración inicial ===
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "asistente"
AI_MODEL = "gemini-2.5-flash"

app = FastAPI(title="ChatPDF API", version="1.0")

# === Inicializar Pinecone y modelo ===
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

llm = ChatGoogleGenerativeAI(model=AI_MODEL, convert_system_message_to_human=True)
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embedding)


# === Funciones utilitarias ===

def hash_archivo(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def ya_existente(file_hash: str) -> bool:
    if not Path("hashes.txt").exists():
        return False
    return file_hash in Path("hashes.txt").read_text().splitlines()

def guardar_hash(file_hash: str):
    with open("hashes.txt", "a") as f:
        f.write(file_hash + "\n")

def leer_pdf_bytes(content: bytes) -> str:
    texto = ""
    with fitz.open(stream=content, filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def fragmentar(texto: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=400)
    return splitter.create_documents([texto])

def vectorizar_documento(texto: str):
    docs = fragmentar(texto)
    PineconeVectorStore.from_documents(docs, index_name=INDEX_NAME, embedding=embedding)

def crear_chain_qa():
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )

def cifrado_cesar(texto: str, desplazamiento: int = 4) -> str:
    resultado = ""
    for c in texto:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            resultado += chr((ord(c) - base + desplazamiento) % 26 + base)
        else:
            resultado += c
    return resultado


# === ENDPOINTS FastAPI ===

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    file_hash = hash_archivo(content)

    if ya_existente(file_hash):
        return {"mensaje": "Este PDF ya fue vectorizado anteriormente."}

    texto = leer_pdf_bytes(content)
    if not texto.strip():
        return JSONResponse(content={"error": "No se pudo extraer texto del PDF."}, status_code=400)

    vectorizar_documento(texto)
    guardar_hash(file_hash)

    return {"mensaje": "PDF procesado y vectorizado correctamente."}


@app.post("/ask")
async def preguntar(pregunta: str = Form(...)):
    pregunta += "\nResponde en español."
    chain = crear_chain_qa()

    inicio = time.perf_counter()
    try:
        with get_openai_callback() as cb:
            respuesta = chain.run(pregunta)
            tiempo = round(time.perf_counter() - inicio, 2)
            respuesta_cifrada = cifrado_cesar(respuesta)

            return {
                "respuesta_cifrada": respuesta_cifrada,
                "tokens_utilizados": cb.total_tokens,
                "tiempo_segundos": tiempo
            }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

