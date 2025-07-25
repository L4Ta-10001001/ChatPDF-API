
## 📘 `README.md` — ChatPDF API con FastAPI, LangChain y Pinecone

# 🧠 ChatPDF API

Servicio web que permite hacer preguntas sobre documentos PDF utilizando **Google Gemini + LangChain** y almacenamiento semántico en **Pinecone**, accesible mediante una API REST desarrollada con **FastAPI**.

> ✅ Adaptado según la rúbrica de evaluación: API en puerto `7650`, procesamiento vectorial, cifrado tipo César, conteo de tokens y tiempo de respuesta.

---

## 🚀 Requisitos

* Python 3.10 o superior (se recomienda usar entorno virtual)
* Claves API:

  * `GOOGLE_API_KEY` (Google Generative AI)
  * `PINECONE_API_KEY` (Pinecone)
* Acceso a internet

---

## ⚙️ Instalación

1. **Clona el repositorio**

```bash
git clone https://github.com/tu-usuario/chatpdf-fastapi.git
cd chatpdf-fastapi
```

2. **Crea y activa un entorno virtual**

```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Instala dependencias**

```bash
pip install -r requirements.txt
```

4. **Crea el archivo `.env` con tus claves**

```env
GOOGLE_API_KEY=tu_clave_google
PINECONE_API_KEY=tu_clave_pinecone
```

---

## ▶️ Ejecución

Inicia el servidor en el puerto `7650`:

```bash
uvicorn main:app --host 0.0.0.0 --port 7650 --reload
```

La API estará disponible en:

```
http://localhost:7650
```

---

## 📤 Endpoints

### ✅ `POST /upload`

Sube un archivo PDF y lo vectoriza (si no ha sido cargado antes).

**Parámetros:**

* `file`: archivo `.pdf`

**Respuesta:**

```json
{
  "mensaje": "PDF procesado y vectorizado correctamente."
}
```

---

### ✅ `POST /ask`

Envía una pregunta en texto sobre el contenido del PDF cargado.

**Parámetros:**

* `pregunta`: texto de la pregunta

**Respuesta:**

```json
{
  "respuesta_cifrada": "Wxvvi xlmw mw xli jsvqypse...",
  "tokens_utilizados": 134,
  "tiempo_segundos": 1.21
}
```

> ℹ️ La respuesta se devuelve cifrada con **César +4**, según solicitud del ejercicio.

---

## 🛠️ Características técnicas

| Requisito                         | ¿Cumplido? | Detalle                                      |
| --------------------------------- | ---------- | -------------------------------------------- |
| API con FastAPI                   | ✅          | Sí, ejecuta en el puerto `7650`              |
| Usa LangChain                     | ✅          | Con `RetrievalQA` y `ChatGoogleGenerativeAI` |
| Usa Pinecone                      | ✅          | Para almacenar los embeddings                |
| Procesamiento y validación de PDF | ✅          | Hash + extracción con PyMuPDF                |
| Chunking con tamaño personalizado | ✅          | `chunk_size=1500`, `overlap=400`             |
| Respuesta cifrada (César +4)      | ✅          | Aplicado a la respuesta final                |
| Tokens usados                     | ✅          | Reportado vía `get_openai_callback()`        |
| Tiempo de ejecución               | ✅          | Cronometrado y mostrado en segundos          |

---

## 🧪 Pruebas rápidas

```bash
# Subir PDF
curl -X POST http://localhost:7650/upload \
  -F "file=@Estatuto_de_la_Universidad_Central_del_Ecuador.pdf"

# Preguntar
curl -X POST http://localhost:7650/ask \
  -F "pregunta=¿Cuál es el objetivo del estatuto?"
```

---

## 🔐 Seguridad

El servicio no guarda archivos PDF, solo el hash y sus vectores. Las claves API deben mantenerse privadas en `.env`.

---

## 🪪 Licencia

MIT License — libre para uso educativo y comercial.

