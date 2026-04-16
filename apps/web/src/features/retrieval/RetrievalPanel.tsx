"use client";

import { useState } from "react";

import type { ApiClient, RetrievalMode, RetrievalResponse } from "../../lib/api";

type Props = {
  api: ApiClient;
  projectId: string | null;
  onAnswer?: (answer: string) => void;
};

const modes: RetrievalMode[] = ["unfiltered", "strict_section", "heading_boosted"];

export function RetrievalPanel({ api, projectId, onAnswer }: Props) {
  const [query, setQuery] = useState("What changed in the implementation plan?");
  const [mode, setMode] = useState<RetrievalMode>("unfiltered");
  const [section, setSection] = useState("Operations");
  const [response, setResponse] = useState<RetrievalResponse | null>(null);
  const [busy, setBusy] = useState(false);

  async function runQuery() {
    if (!projectId || !query.trim()) {
      return;
    }
    setBusy(true);
    try {
      const next = await api.queryRetrieval({
        project_id: projectId,
        query: query.trim(),
        mode,
        section_path_prefix: mode === "strict_section" ? section : undefined,
        limit: 5,
      });
      setResponse(next);
      onAnswer?.(next.results[0]?.text ?? "No matching project context found.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel retrieval-panel" aria-label="Retrieval">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Retrieval</p>
          <h2>Project search</h2>
        </div>
        {response?.degraded ? <span className="status-chip warning">Lexical</span> : null}
      </div>
      <textarea value={query} onChange={(event) => setQuery(event.target.value)} rows={3} />
      <div className="segmented" aria-label="Retrieval mode">
        {modes.map((item) => (
          <button
            type="button"
            key={item}
            className={item === mode ? "active" : ""}
            onClick={() => setMode(item)}
          >
            {item.replace("_", " ")}
          </button>
        ))}
      </div>
      {mode === "strict_section" ? (
        <input value={section} onChange={(event) => setSection(event.target.value)} />
      ) : null}
      <button type="button" className="primary-action" onClick={runQuery} disabled={busy || !projectId}>
        {busy ? "Searching" : "Search"}
      </button>
      {response ? (
        <div className="results-list">
          {response.results.map((result) => (
            <article key={`${result.source_type}-${result.source_id}`}>
              <div className="panel-title-row">
                <strong>{result.title}</strong>
                <span className="score">{Math.round(result.score * 100)}%</span>
              </div>
              <p>{result.text}</p>
              <small>
                {result.citation.heading_path_text ?? result.citation.section_path ?? result.source_type}
              </small>
            </article>
          ))}
          {!response.results.length ? <p className="empty-state">No matches returned.</p> : null}
        </div>
      ) : null}
    </section>
  );
}
