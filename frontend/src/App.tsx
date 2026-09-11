import { useState } from "react";
import "./App.css";

type Message = {
  role: "user" | "assistant";
  content: string;
};

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmedMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedMessage,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.message,
        },
      ]);
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Unable to reach the assistant.";

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    sendMessage();
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Replicant Payments Assistant</h1>
          <p>AI-powered payments operations</p>
        </div>
      </header>

      <main className="chat-container">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>How can I help?</h2>
            <p>
              Ask me to manage payments, create invoices, or analyze
              payment activity.
            </p>

            <div className="examples">
              <button
                onClick={() => setMessage("What is today's payment summary?")}
              >
                Today's payment summary
              </button>

              <button
                onClick={() => setMessage("Refund Maya's last payment")}
              >
                Refund Maya's last payment
              </button>

              <button
                onClick={() =>
                  setMessage(
                    "Create a $250 invoice for Acme Corp due next Friday",
                  )
                }
              >
                Create an invoice
              </button>

              <button
                onClick={() =>
                  setMessage(
                    "How much did we take this week compared to last week?",
                  )
                }
              >
                Compare weekly payments
              </button>
            </div>
          </div>
        )}

        <div className="messages">
          {messages.map((item, index) => (
            <div
              key={index}
              className={`message-row ${item.role}`}
            >
              <div className="message">
                {item.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="message loading">
                Thinking...
              </div>
            </div>
          )}
        </div>
      </main>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about payments, refunds, invoices..."
          disabled={loading}
        />

        <button
          type="submit"
          disabled={!message.trim() || loading}
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default App;