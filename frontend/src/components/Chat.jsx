import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { askQuestion } from "../api";

const SUGGESTIONS = [
  "Summarize this document",
  "What are the main topics covered?",
  "What are the key conclusions?",
];

export default function Chat({ doc, messages, setMessages }) {
  const [input, setInput] = useState("");
  const [asking, setAsking] = useState(false);
  const bottomRef = useRef(null);

  // Scroll to the newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  async function send(text) {
    const question = (text ?? input).trim();
    if (!question || asking) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setAsking(true);

    try {
      const data = await askQuestion(question, doc.doc_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, pages: data.pages },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: err.message, error: true },
      ]);
    } finally {
      setAsking(false);
    }
  }

  function handleKeyDown(e) {
    // Enter sends, Shift+Enter makes a new line
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>Your PDF is ready</h2>
            <p>
              {doc.pages} pages indexed into {doc.chunks} chunks. Ask anything about it.
            </p>
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip-button" onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`message-row ${m.role}`}>
            <div className={`bubble ${m.role} ${m.error ? "error" : ""}`}>
              {m.role === "assistant" && !m.error ? (
                <ReactMarkdown>{m.text}</ReactMarkdown>
              ) : (
                <p>{m.text}</p>
              )}

              {m.pages && m.pages.length > 0 && (
                <div className="sources">
                  <span className="sources-label">Sources</span>
                  {m.pages.map((p) => (
                    <span key={p} className="page-chip">
                      Page {p}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {asking && (
          <div className="message-row assistant">
            <div className="bubble assistant typing">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <textarea
          rows={1}
          value={input}
          placeholder="Ask a question about your PDF..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={asking}
        />
        <button className="send-button" onClick={() => send()} disabled={asking || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}