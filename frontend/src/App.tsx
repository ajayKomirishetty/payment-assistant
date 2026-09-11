import { useState } from "react";
import "./App.css";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const quickActions = [
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

  const clearConversation = () => {
    setMessages([]);
    setMessage("");
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-mark">R</div>

          <div>
            <div className="brand-name">Replicant</div>
            <div className="brand-subtitle">Payments Operations</div>
          </div>
        </div>

        {messages.length > 0 && (
          <button className="clear-button" onClick={clearConversation}>
            Clear conversation
          </button>
        )}
      </header>

      <main className="chat-container">
        {messages.length === 0 ? (
          <section className="welcome">
            <div className="status-badge">
              <span className="status-dot" />
              Payments assistant online
            </div>

            <h1>
              Your payments,
              <br />
              <span>simplified.</span>
            </h1>

            <p className="welcome-description">
              Manage payments, refunds, invoices, and payment activity
              using natural language.
            </p>

            <div className="examples">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  className="example-card"
                  onClick={() => setMessage(action.prompt)}
                >
                  <span>{action.label}</span>
                  <span className="arrow">→</span>
                </button>
              ))}
            </div>
          </section>
        ) : (
          <section className="conversation">
            <div className="conversation-header">
              <div>
                <span className="eyebrow">CONVERSATION</span>
                <h2>Payments assistant</h2>
              </div>

              <div className="online-indicator">
                <span />
                Online
              </div>
            </div>

            <div className="messages">
              {messages.map((item, index) => (
                <div
                  key={index}
                  className={`message-row ${item.role}`}
                >
                  {item.role === "assistant" && (
                    <div className="assistant-avatar">R</div>
                  )}

                  <div className="message-wrapper">
                    <div className="message-label">
                      {item.role === "assistant" ? "Replicant" : "You"}
                    </div>

                    <div className="message">{item.content}</div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant">
                  <div className="assistant-avatar">R</div>

                  <div className="message-wrapper">
                    <div className="message-label">Replicant</div>

                    <div className="message loading">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      <div className="composer-wrapper">
        <div className="quick-prompts">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => sendMessage(action.prompt)}
              disabled={loading}
            >
              {action.label}
            </button>
          ))}
        </div>

        <form className="input-area" onSubmit={handleSubmit}>
          <div className="input-icon">✦</div>

          <input
            type="text"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask about payments, refunds, invoices..."
            disabled={loading}
          />

          <button
            className="send-button"
            type="submit"
            disabled={!message.trim() || loading}
            aria-label="Send message"
          >
            {loading ? "…" : "↑"}
          </button>
        </form>

        <p className="composer-hint">
          Press <strong>Enter</strong> to send · AI responses are based on
          your payment data
        </p>
      </div>
    </div>
  );
}

export default App;