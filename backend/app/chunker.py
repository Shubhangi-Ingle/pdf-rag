from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents, chunk_size: int = 1000, chunk_overlap: int = 200):
    """Split page-level Documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,  # saves where each chunk starts in its page
    )
    chunks = splitter.split_documents(documents)
    return chunks