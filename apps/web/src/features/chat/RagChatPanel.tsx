"use client";

import { useState } from "react";

import type { ApiClient } from "../../lib/api";

type Props = {
  api: ApiClient;
  projectId: string | null;
  lastRetrievedAnswer: string | null;
};

type Message = { role: "user" | "assistant"; body: string };

export function RagChatPanel({ api, projectId, lastRetrievedAnswer }: Props) {
  const [prompt, setPrompt] = useState("Summarize the strongest source.");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!projectId || !prompt.trim()) {
      return;
    }
    const userMessage: Message = { role: "user", body: prompt.trim() };
    setMessages((current) => [...current, userMessage]);
    setBusy(true);
    try {
      const response = await api.queryRetrieval({
        project_id: projectId,
        query: prompt.trim(),
        mode: "heading_boosted",
        limit: 3,
      });
      const answer =
        response.results[0]?.text ??
        lastRetrievedAnswer ??
        "No matching project knowledge is available yet.";
      setMessages((current) => [...current, { role: "assistant", body: answer }]);
      setPrompt("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel chat-panel" aria-label="RAG chat">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Chat</p>
          <h2>RAG assistant</h2>
        </div>
      </div>
      <div className="message-list">
        {messages.map((message, index) => (
          <p key={`${message.role}-${index}`} className={message.role}>
            {message.body}
          </p>
        ))}
        {!messages.length ? <p className="empty-state">Ask a project-scoped question.</p> : null}
      </div>
      <div className="inline-form">
        <input value={prompt} onChange={(event) => setPrompt(event.target.value)} />
        <button type="button" onClick={send} disabled={busy || !projectId}>
          Send
        </button>
      </div>
    </section>
  );
}
