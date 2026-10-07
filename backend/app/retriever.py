from app.vectorstore import get_vectorstore


def get_retriever(k: int = 4, search_type: str = "similarity", source: str | None = None):
    """Wrap Chroma as a retriever, optionally limited to one PDF."""
    vectorstore = get_vectorstore()

    search_kwargs = {"k": k}
    if search_type == "mmr":
        search_kwargs["fetch_k"] = 30       # look at more candidates
        search_kwargs["lambda_mult"] = 0.3  # lower = more variety
    if source:
        search_kwargs["filter"] = {"source": source}

    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs,
    )