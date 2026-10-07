import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.embeddings import get_embedding_model
from app.vectorstore import get_vectorstore
from app.ingest import ingest_pdf
from app.rag_chain import answer_question

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_MB = 20


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: load the heavy objects now,
    # so the first user request isn't slow
    get_embedding_model()
    get_vectorstore()
    yield


app = FastAPI(title="PDF RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    doc_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    # 1. Validate
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    content = file.file.read()
    if len(content) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File is larger than {MAX_FILE_MB} MB.")

    # 2. Save with a unique id, so two files with the same name don't clash
    doc_id = uuid.uuid4().hex
    save_path = UPLOAD_DIR / f"{doc_id}.pdf"
    save_path.write_bytes(content)

    # 3. Run the ingestion pipeline
    try:
        result = ingest_pdf(str(save_path))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not read this PDF: {e}")

    if result["chunks"] == 0:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="No text found in this PDF. It may be a scanned document.",
        )

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "pages": result["pages"],
        "chunks": result["chunks"],
    }


@app.post("/ask")
def ask(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # The doc_id must match a file we saved
    pdf_path = UPLOAD_DIR / f"{req.doc_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Document not found. Please upload it again.")

    try:
        return answer_question(question, source=str(pdf_path))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The AI service is busy right now. Please try again in a moment.",
        )