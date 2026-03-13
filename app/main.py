from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
import uuid

from app.rag import ingest_pdf, query_document

app = FastAPI(
    title="DocuMind API",
    description="AI-powered Document Q&A — Upload any PDF and ask questions about it using RAG.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store of session_id -> vectorstore path
sessions: dict = {}


class QueryRequest(BaseModel):
    session_id: str
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str


@app.get("/")
def root():
    return {
        "message": "Welcome to DocuMind API 🧠",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /upload",
            "query": "POST /query",
            "health": "GET /health",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file. Returns a session_id to use for querying.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    session_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        vectorstore_path = ingest_pdf(file_path, session_id)
        sessions[session_id] = vectorstore_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    return {
        "message": "PDF uploaded and processed successfully ✅",
        "session_id": session_id,
        "filename": file.filename,
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Ask a question about an uploaded PDF using its session_id.
    """
    if request.session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload a PDF first.",
        )

    try:
        result = query_document(
            vectorstore_path=sessions[request.session_id],
            question=request.question,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=request.session_id,
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
