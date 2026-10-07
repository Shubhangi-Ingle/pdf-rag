from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.retriever import get_retriever
from app.llm import get_llm

NOT_FOUND_TEXT = "I couldn't find this in the document."

PROMPT = ChatPromptTemplate.from_template(
    """You are an assistant that answers questions about a PDF document, using the excerpts below.

Rules:
- Start with the answer itself. Never begin with phrases like "Based on the document" or "According to the context".
- Use ONLY the excerpts. If they do not contain the answer, reply exactly: "I couldn't find this in the document."
- If the excerpts answer only part of the question, give that part and say what is missing.
- Be specific: include the names, numbers and technical terms that appear in the excerpts.
- Use short paragraphs, or bullet points when listing several items.
- Ignore page headers, footers and DOI lines.
- For broad questions (such as "what are the applications of..."), cover every relevant item found in the excerpts, grouped by topic, instead of giving a short overview.
Excerpts:
{context}

Question: {question}

Answer:"""
)


def format_docs(docs):
    """Join the retrieved chunks into one context string, labelled by page."""
    parts = []
    for doc in docs:
        page = doc.metadata["page"] + 1
        parts.append(f"[Page {page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def answer_question(
    question: str,
    source: str | None = None,
    k: int = 6,
    search_type: str = "mmr",
):
    """Run the full RAG pipeline: retrieve -> prompt -> LLM -> answer + sources."""
    retriever = get_retriever(k=k, search_type=search_type, source=source)
    docs = retriever.invoke(question)

    chain = PROMPT | get_llm() | StrOutputParser()
    answer = chain.invoke({
        "context": format_docs(docs),
        "question": question,
    })

    # If the model says it couldn't find the answer, don't show misleading sources
    if NOT_FOUND_TEXT in answer:
        pages = []
    else:
        pages = sorted({doc.metadata["page"] + 1 for doc in docs})

    return {"answer": answer, "pages": pages}