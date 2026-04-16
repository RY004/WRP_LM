"use client";

import { useState } from "react";

import type { ApiClient, PipelineRead } from "../../lib/api";

type Props = {
  api: ApiClient;
  projectId: string | null;
  pipeline: PipelineRead | null;
  onRefresh: () => Promise<void>;
};

export function PipelinePanel({ api, projectId, pipeline, onRefresh }: Props) {
  const [note, setNote] = useState("Looks ready from the product surface.");
  const [handoff, setHandoff] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function run(action: string, task: () => Promise<unknown>) {
    if (!projectId) {
      return;
    }
    setBusy(action);
    try {
      await task();
      await onRefresh();
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="panel pipeline-panel" aria-label="Pipeline">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Pipeline</p>
          <h2>{pipeline ? pipeline.current_stage : "No project selected"}</h2>
        </div>
        {pipeline ? <span className="status-chip">{pipeline.status}</span> : null}
      </div>
      {pipeline ? (
        <>
          <div className="metric-row">
            <div>
              <small>Cycle</small>
              <strong>{pipeline.cycle}</strong>
            </div>
            <div>
              <small>Branch</small>
              <strong>{pipeline.branch_name}</strong>
            </div>
          </div>
          <textarea value={note} onChange={(event) => setNote(event.target.value)} rows={3} />
          <div className="button-row">
            <button
              type="button"
              onClick={() => run("approve", () => api.approvePipeline(pipeline.project_id, note))}
              disabled={busy !== null}
            >
              Approve
            </button>
            <button
              type="button"
              onClick={() => run("reject", () => api.rejectPipeline(pipeline.project_id, note))}
              disabled={busy !== null}
            >
              Reject
            </button>
            <button
              type="button"
              onClick={() => run("advance", () => api.advancePipeline(pipeline.project_id, false))}
              disabled={busy !== null}
            >
              Advance
            </button>
            <button
              type="button"
              onClick={() =>
                run("handoff", async () => setHandoff(await api.handoffPacket(pipeline.project_id)))
              }
              disabled={busy !== null}
            >
              Handoff
            </button>
          </div>
          {handoff ? <pre className="handoff">{JSON.stringify(handoff, null, 2)}</pre> : null}
        </>
      ) : (
        <p className="empty-state">Create or select a project to view pipeline state.</p>
      )}
    </section>
  );
}
