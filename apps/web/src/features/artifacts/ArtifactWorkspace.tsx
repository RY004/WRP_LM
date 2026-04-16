"use client";

import { useEffect, useMemo, useState } from "react";

import type { ApiClient, ArtifactCommentRead, ArtifactRead, ArtifactVersionRead } from "../../lib/api";
import { downloadArtifactMarkdown, downloadBulkMarkdown } from "../../lib/export";

type Props = {
  api: ApiClient;
  projectId: string | null;
  artifacts: ArtifactRead[];
  onRefresh: () => Promise<void>;
};

export function ArtifactWorkspace({ api, projectId, artifacts, onRefresh }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [title, setTitle] = useState("Implementation Notes");
  const [markdown, setMarkdown] = useState("# Implementation Notes\n\nCapture the decision here.");
  const [comment, setComment] = useState("Review this before approval.");
  const [comments, setComments] = useState<ArtifactCommentRead[]>([]);
  const [versions, setVersions] = useState<ArtifactVersionRead[]>([]);
  const [busy, setBusy] = useState(false);

  const selected = useMemo(
    () => artifacts.find((artifact) => artifact.id === selectedId) ?? artifacts[0] ?? null,
    [artifacts, selectedId],
  );

  useEffect(() => {
    if (!selected) {
      return;
    }
    setSelectedId(selected.id);
    setTitle(selected.title);
    setMarkdown(selected.rendered_markdown);
    void Promise.all([api.listComments(selected.id), api.listVersions(selected.id)]).then(
      ([nextComments, nextVersions]) => {
        setComments(nextComments);
        setVersions(nextVersions);
      },
    );
  }, [api, selected]);

  async function save() {
    if (!projectId) {
      return;
    }
    setBusy(true);
    try {
      if (selected) {
        await api.updateArtifact(selected.id, {
          title,
          markdown,
          change_summary: "Edited from web workspace",
        });
      } else {
        await api.createArtifact({
          project_id: projectId,
          title,
          artifact_type: "document",
          markdown,
          stage: "implement",
        });
      }
      await onRefresh();
    } finally {
      setBusy(false);
    }
  }

  async function addComment() {
    if (!selected || !comment.trim()) {
      return;
    }
    const next = await api.addComment(selected.id, comment.trim());
    setComments((current) => [next, ...current]);
    setComment("");
  }

  return (
    <section className="panel artifact-workspace" aria-label="Artifacts">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Artifacts</p>
          <h2>Authoring</h2>
        </div>
        <button type="button" onClick={() => downloadBulkMarkdown(artifacts)} disabled={!artifacts.length}>
          Export all
        </button>
      </div>
      <div className="artifact-layout">
        <aside className="artifact-list" aria-label="Artifact list">
          {artifacts.map((artifact) => (
            <button
              type="button"
              key={artifact.id}
              className={artifact.id === selected?.id ? "artifact-item active" : "artifact-item"}
              onClick={() => setSelectedId(artifact.id)}
            >
              <span>{artifact.title}</span>
              <small>v{artifact.current_version_number}</small>
            </button>
          ))}
          {!artifacts.length ? <p className="empty-state">No artifacts yet.</p> : null}
        </aside>
        <div className="editor-column">
          <input value={title} onChange={(event) => setTitle(event.target.value)} />
          <textarea value={markdown} onChange={(event) => setMarkdown(event.target.value)} rows={11} />
          <div className="button-row">
            <button type="button" className="primary-action" onClick={save} disabled={busy || !projectId}>
              {selected ? "Save version" : "Create artifact"}
            </button>
            <button type="button" onClick={() => selected && downloadArtifactMarkdown(selected)} disabled={!selected}>
              Export
            </button>
          </div>
        </div>
        <aside className="review-column" aria-label="Review">
          <h3>Versions</h3>
          <div className="compact-list">
            {versions.map((version) => (
              <span key={version.id}>v{version.version_number} {version.change_summary ?? ""}</span>
            ))}
          </div>
          <h3>Comments</h3>
          <div className="inline-form stacked">
            <textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={3} />
            <button type="button" onClick={addComment} disabled={!selected}>
              Comment
            </button>
          </div>
          <div className="compact-list">
            {comments.map((item) => (
              <span key={item.id}>{item.body}</span>
            ))}
          </div>
        </aside>
      </div>
      <p className="boundary-note">Exports are markdown packages for manual Notion import.</p>
    </section>
  );
}
