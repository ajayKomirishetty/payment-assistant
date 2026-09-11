import { useEffect, useRef, useState } from "react";
import "./App.css";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const suggestions = [
  {
    label: "Today's summary",
    prompt: "What is today's payment summary?",
  },
  {
    label: "Compare payments",
    prompt: "How much did we take this week compared to last week?",
  },
  {
    label: "Create invoice",
    prompt: "Create a $250 invoice for Acme Corp due next Friday",
  },
  {
    label: "Refund payment",
    prompt: "Refund Maya's last payment",
  },
];

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const sendMessage = async (text?: string) => {
    const trimmedMessage = (text ?? message).trim();

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
      const response = await fetch(
        "http://localhost:8000/api/assistant",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: trimmedMessage,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Something went wrong.",
        );
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            data.message || "The request completed successfully.",
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

  const handleSubmit = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    sendMessage();
  };

  const handleSuggestion = (prompt: string) => {
    setMessage(prompt);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-mark">R</div>

          <div>
            <h1>Replicant</h1>
            <p>Payments Assistant</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot" />
          Stripe connected
        </div>
      </header>

      <main className="chat-container">
        {messages.length === 0 ? (
          <div className="welcome">
            <div className="welcome-mark">R</div>

            <p className="eyebrow">REPLICANT</p>

            <h2>How can I help?</h2>

            <p className="welcome-description">
              Manage payments, invoices, refunds, and payment
              activity using natural language.
            </p>
          </div>
        ) : (
          <div className="messages">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`message-row ${item.role}`}
              >
                {item.role === "assistant" && (
                  <div className="message-avatar">R</div>
                )}

                <div className="message-wrapper">
                  <div className="message-label">
                    {item.role === "assistant"
                      ? "REPLICANT"
                      : "YOU"}
                  </div>

                  <div className="message">
                    {item.content}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row assistant">
                <div className="message-avatar">R</div>

                <div className="message-wrapper">
                  <div className="message-label">REPLICANT</div>

                  <div className="message loading">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <section className="composer">
        <div className="suggestions">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.label}
              type="button"
              onClick={() =>
                handleSuggestion(suggestion.prompt)
              }
              disabled={loading}
            >
              {suggestion.label}
            </button>
          ))}
        </div>

        <form
          className="input-form"
          onSubmit={handleSubmit}
        >
          <span className="input-icon">✦</span>

          <input
            type="text"
            value={message}
            onChange={(event) =>
              setMessage(event.target.value)
            }
            placeholder="Ask another question..."
            disabled={loading}
          />

          <button
            className="send-button"
            type="submit"
            disabled={!message.trim() || loading}
            aria-label="Send message"
          >
            ↑
          </button>
        </form>
      </section>
    </div>
  );
}

export default App;