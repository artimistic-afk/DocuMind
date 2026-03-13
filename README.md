# 🧠 DocuMind — AI Document Q&A API

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-LLaMA3-F55036?style=for-the-badge&logo=groq&logoColor=white"/>
  <img src="https://img.shields.io/badge/FAISS-Vector Store-0064a5?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
</p>

<p align="center">
  <b>Upload any PDF → Ask questions → Get AI-powered answers with source citations.</b><br/>
  Built with RAG (Retrieval-Augmented Generation), FastAPI, LangChain, FAISS, and Groq LLaMA3.
</p>

---

## 📌 What is DocuMind?

DocuMind is a production-ready REST API that lets you interact with any PDF document using natural language. It uses **RAG (Retrieval-Augmented Generation)** to retrieve the most relevant chunks from your document and pass them to an LLM for accurate, grounded answers — with page citations included.

**Real-world use cases:**
- Ask questions about research papers
- Query legal contracts or financial reports
- Extract insights from technical documentation
- Build custom document chatbots

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENT                             │
│              (curl / Postman / Frontend)                │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI SERVER                        │
│                                                         │
│   POST /upload              POST /query                 │
│        │                         │                      │
│        ▼                         ▼                      │
│  ┌──────────────┐      ┌──────────────────────┐        │
│  │  PDF Loader  │      │  Question Received    │        │
│  │  (PyPDF)     │      └──────────┬───────────┘        │
│  └──────┬───────┘                 │                     │
│         ▼                         ▼                     │
│  ┌──────────────┐      ┌──────────────────────┐        │
│  │ Text Splitter│      │  FAISS Retriever      │        │
│  │ (1000 chars) │      │  (Top-4 chunks)       │        │
│  └──────┬───────┘      └──────────┬───────────┘        │
│         ▼                         ▼                     │
│  ┌──────────────┐      ┌──────────────────────┐        │
│  │  HuggingFace │      │  Groq LLaMA 3.1      │        │
│  │  Embeddings  │      │  (Answer Generation)  │        │
│  └──────┬───────┘      └──────────┬───────────┘        │
│         ▼                         ▼                     │
│  ┌──────────────┐      ┌──────────────────────┐        │
│  │  FAISS Index │      │  Answer + Sources     │        │
│  │  (Saved)     │      │  (JSON Response)      │        │
│  └──────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/artimistic-afk/DocuMind.git
cd DocuMind

# 2. Set up your API key
cp .env.example .env
# Edit .env and add your Groq API key (free at console.groq.com)

# 3. Run with Docker
docker-compose up --build
```

API is live at `http://localhost:8000` 🎉

---

### Option 2 — Local Python

```bash
# 1. Clone and enter directory
git clone https://github.com/artimistic-afk/DocuMind.git
cd DocuMind

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Add your Groq API key to .env

# 5. Run the server
uvicorn app.main:app --reload
```

---

## 🔑 Get Your Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Create an API key
4. Paste it into your `.env` file

---

## 📡 API Reference

### `GET /` — Welcome
Returns API info and available endpoints.

---

### `GET /health` — Health Check
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### `POST /upload` — Upload PDF

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "message": "PDF uploaded and processed successfully ✅",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "your_document.pdf"
}
```

---

### `POST /query` — Ask a Question

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "question": "What are the main findings of this document?"
  }'
```

**Response:**
```json
{
  "answer": "The main findings include...",
  "sources": ["Page 3", "Page 7", "Page 12"],
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | REST API with auto docs |
| RAG Orchestration | LangChain | Document loading, chunking, chaining |
| Vector Store | FAISS (Facebook AI) | Similarity search over embeddings |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Free, local embedding model |
| LLM | Groq LLaMA 3.1-8B | Fast, free answer generation |
| PDF Parsing | PyPDF | Extract text from PDFs |
| Containerization | Docker + Docker Compose | One-command deployment |

---

## 📁 Project Structure

```
DocuMind/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, routes, request handling
│   └── rag.py           # RAG pipeline: ingest + query logic
├── uploads/             # Uploaded PDFs (gitignored)
├── vectorstore/         # FAISS indexes (gitignored)
├── Dockerfile           # Container definition
├── docker-compose.yml   # Multi-service orchestration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore
└── README.md
```

---

## 💡 How RAG Works (Simply Explained)

Traditional LLMs hallucinate because they rely only on training data. RAG fixes this:

1. **Ingest** — Your PDF is split into ~1000 character chunks
2. **Embed** — Each chunk is converted to a vector (numerical representation)
3. **Store** — Vectors are saved in FAISS for fast similarity search
4. **Retrieve** — When you ask a question, the 4 most relevant chunks are fetched
5. **Generate** — The LLM reads only those chunks and answers accurately

---

## 🔮 Future Improvements

- [ ] Support for multiple file formats (DOCX, TXT, CSV)
- [ ] Persistent session storage with Redis
- [ ] Streaming responses for faster UX
- [ ] Frontend UI with React
- [ ] Authentication with API keys
- [ ] Support for multiple documents per session

---

## 👤 Author

**Abdurrahman Tahir** — ML Engineer & Data Scientist

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/abdurrahmantahir79/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/artimistic-afk)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-14b8a6?style=flat)](https://abdurrahmantahir.vercel.app)

---

## 📄 License

MIT License — free to use, modify, and distribute.
