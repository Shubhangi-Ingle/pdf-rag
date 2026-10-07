import { useRef, useState } from "react";
import { uploadPdf } from "../api";

export default function UploadCard({ onUploaded }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleFile(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF file.");
      return;
    }
    setError("");
    setUploading(true);
    try {
      const doc = await uploadPdf(file);
      onUploaded(doc);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }

  return (
    <div className="upload-wrap">
      <h1 className="upload-title">Chat with your PDF</h1>
      <p className="upload-subtitle">
        Upload a document and ask questions. Answers come only from your file,
        with the page numbers they were found on.
      </p>

      <div
        className={`dropzone ${dragging ? "dragging" : ""} ${uploading ? "disabled" : ""}`}
        onClick={() => !uploading && inputRef.current.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {uploading ? (
          <>
            <div className="spinner" />
            <p className="dropzone-main">Reading and indexing your PDF...</p>
            <p className="dropzone-hint">This can take a few seconds for large files</p>
          </>
        ) : (
          <>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
              <path d="M14 3v5h5" />
              <path d="M12 17v-6" />
              <path d="m9.5 13.5 2.5-2.5 2.5 2.5" />
            </svg>
            <p className="dropzone-main">Click to choose a PDF, or drag it here</p>
            <p className="dropzone-hint">Text-based PDFs only, up to 20 MB</p>
          </>
        )}
      </div>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}