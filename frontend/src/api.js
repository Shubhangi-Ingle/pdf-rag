const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Turn any error response from FastAPI into a readable message
async function handleResponse(res) {
  if (res.ok) return res.json();

  let message = "Something went wrong. Please try again.";
  try {
    const data = await res.json();
    if (typeof data.detail === "string") message = data.detail;
  } catch {
    // response had no JSON body, keep the default message
  }
  throw new Error(message);
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file); // must match the parameter name "file" in FastAPI

  try {
    const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
    return await handleResponse(res);
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error("Cannot reach the server. Is the backend running?");
    }
    throw err;
  }
}

export async function askQuestion(question, docId) {
  try {
    const res = await fetch(`${API_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, doc_id: docId }),
    });
    return await handleResponse(res);
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error("Cannot reach the server. Is the backend running?");
    }
    throw err;
  }
}