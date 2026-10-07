from app.loader import load_pdf
from app.chunker import split_documents
from app.vectorstore import add_chunks


def ingest_pdf(file_path: str):
    """Load a PDF, split it into chunks, embed and store them. Returns counts."""
    docs = load_pdf(file_path)
    chunks = split_documents(docs)

    # Scanned PDFs have no extractable text
    if not chunks or not any(c.page_content.strip() for c in chunks):
        return {"pages": len(docs), "chunks": 0}

    add_chunks(chunks)
    return {"pages": len(docs), "chunks": len(chunks)}