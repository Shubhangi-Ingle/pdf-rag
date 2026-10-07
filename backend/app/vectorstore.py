from functools import lru_cache
from pathlib import Path
from langchain_chroma import Chroma
from app.embeddings import get_embedding_model

CHROMA_DIR = str(Path(__file__).resolve().parent.parent / "data" / "chroma_db")
COLLECTION_NAME = "pdf_chunks"


@lru_cache(maxsize=1)
def get_vectorstore():
    """Open (or create) the Chroma collection once and reuse it."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=CHROMA_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunks):
    """Embed the chunks and store them in Chroma."""
    vectorstore = get_vectorstore()

    ids = [
        f"{c.metadata['source']}-p{c.metadata['page']}-s{c.metadata['start_index']}"
        for c in chunks
    ]
    vectorstore.add_documents(chunks, ids=ids)
    return vectorstore