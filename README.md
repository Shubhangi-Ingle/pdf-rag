# PDF RAG: Chat with Your PDF

A Retrieval-Augmented Generation (RAG) application. Upload a PDF, ask questions in plain language, and get answers grounded **only in your document**, with the page numbers they came from.

Built step by step as a hands-on way to learn the full RAG pipeline with **LangChain**, **ChromaDB**, **Gemini**, **FastAPI** and **React**.

## Features

- Upload a text-based PDF and have it indexed automatically
- Ask questions and get answers based only on the document's content
- Page citations shown under every answer
- Honest "not found" replies when the document does not contain the answer
- Each upload is isolated, so questions only search the PDF you uploaded
- Clean chat interface with Markdown-formatted answers and suggested questions

## How it works

```
INGESTION (when you upload a PDF)

  PDF  ->  Load pages  ->  Split into chunks  ->  Embed chunks  ->  Store in ChromaDB


QUESTION ANSWERING (every time you ask)

  Question  ->  Embed question  ->  Search ChromaDB  ->  Top chunks
                                                            |
                                  Answer + page numbers  <-  Prompt + Gemini
```

| Stage | What happens | Tool |
|---|---|---|
| Load | Extract text from each page, keeping the page number | LangChain `PyPDFLoader` |
| Chunk | Split text into ~1000-character pieces with 200 characters of overlap | `RecursiveCharacterTextSplitter` |
| Embed | Convert each chunk into a 384-dimensional vector | `all-MiniLM-L6-v2` (local, free) |
| Store | Save vectors, text and metadata to disk | ChromaDB |
| Retrieve | Find the most relevant, diverse chunks (MMR, k=6) from the uploaded PDF only | LangChain retriever |
| Generate | Answer strictly from the retrieved chunks, or say it is not in the document | Gemini via LangChain (LCEL) |

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| RAG | LangChain, sentence-transformers, ChromaDB |
| LLM | Google Gemini (free tier) |
| Frontend | React, Vite, react-markdown |

## Getting started

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- A free Gemini API key from https://aistudio.google.com/apikey

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/pdf-rag.git
cd pdf-rag
```

### 2. Start the backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a file named `.env` inside `backend/` (copy `.env.example`) and add your key:

```
GEMINI_API_KEY=your_key_here
```

Run the server:

```bash
uvicorn app.main:app --reload
```

The first start downloads the embedding model (about 90 MB) and takes 20 to 30 seconds. The API is ready when you see `Application startup complete`.

### 3. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

## API reference

Interactive documentation is available at http://127.0.0.1:8000/docs while the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload a PDF (multipart form field `file`). Returns `doc_id`, `filename`, `pages`, `chunks` |
| `POST` | `/ask` | Body: `{"question": "...", "doc_id": "..."}`. Returns `answer` and a list of source `pages` |

Example response from `/ask`:

```json
{
  "answer": "Convolutional neural networks are ...",
  "pages": [1, 2, 3]
}
```

## Project structure

```
pdf-rag/
├── backend/
│   ├── app/
│   │   ├── main.py          FastAPI app and endpoints
│   │   ├── loader.py        PDF loading
│   │   ├── chunker.py       Text splitting
│   │   ├── embeddings.py    Embedding model (cached)
│   │   ├── vectorstore.py   ChromaDB setup (cached)
│   │   ├── ingest.py        Load -> chunk -> embed -> store
│   │   ├── retriever.py     Search settings (similarity / MMR)
│   │   ├── llm.py           Gemini client (cached)
│   │   └── rag_chain.py     Prompt, generation and citations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── api.js           Backend calls
│       ├── App.jsx
│       └── components/      UploadCard, Chat
└── README.md
```

## Design decisions

- **Plain functions first, LangChain components inside.** Each pipeline stage lives in its own small module so it is easy to read, test and swap.
- **Metadata filtering.** Every chunk stores the path of its source file, and each question is filtered to the uploaded PDF, so documents never mix.
- **Strict prompt.** The model is told to answer only from the retrieved excerpts and to reply "I couldn't find this in the document." otherwise. Source pages are hidden in that case.
- **MMR retrieval.** Maximal Marginal Relevance with a wider candidate pool returns chunks from more parts of the document than plain similarity search.
- **Cached heavy objects.** The embedding model, vector store and LLM client are created once, which removes repeated 20+ second delays.
- **Loaded at startup.** The embedding model loads when the server starts, so the first user request is fast.

## What I learned

- Chunk size and overlap decide whether an idea stays intact. Too small loses context, too large exceeds the embedding model's input limit.
- Answer quality depends on retrieval. The LLM can only use what it is given, and short, vague questions tend to match summary sentences rather than detailed sections.
- Prompt wording controls hallucination and tone as much as the model does.
- Embedding search matches meaning, not keywords. A vector database makes that search fast and persistent.

## Limitations

- Scanned (image-only) PDFs are not supported, because there is no OCR
- Page headers and footers are embedded as noise inside chunks
- Broad requests such as "summarize the whole document" only see the top chunks
- No conversation memory: each question is answered independently
- Answers reflect the source document's own wording
- Uploaded files and vectors are not deleted automatically

