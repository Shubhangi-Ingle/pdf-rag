import { useState } from "react";
import UploadCard from "./components/UploadCard";
import Chat from "./components/Chat";
import "./App.css";

export default function App() {
  const [doc, setDoc] = useState(null); // { doc_id, filename, pages, chunks }
  const [messages, setMessages] = useState([]);

  function handleUploaded(newDoc) {
    setDoc(newDoc);
    setMessages([]);
  }

  function handleReset() {
    setDoc(null);
    setMessages([]);
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <span className="brand-mark">R</span>
          <span className="brand-name">PDF RAG</span>
        </div>

        {doc && (
          <div className="doc-info">
            <span className="doc-name" title={doc.filename}>
              {doc.filename}
            </span>
            <button className="ghost-button" onClick={handleReset}>
              Upload new PDF
            </button>
          </div>
        )}
      </header>

      <main className="main">
        {doc ? (
          <Chat doc={doc} messages={messages} setMessages={setMessages} />
        ) : (
          <UploadCard onUploaded={handleUploaded} />
        )}
      </main>
    </div>
  );
}