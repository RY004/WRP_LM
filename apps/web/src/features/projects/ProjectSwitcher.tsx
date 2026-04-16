"use client";

import { useState } from "react";

import type { ProjectRead } from "../../lib/api";

type Props = {
  projects: ProjectRead[];
  selectedProjectId: string | null;
  onSelect: (projectId: string) => void;
  onCreate: (name: string) => Promise<void>;
};

export function ProjectSwitcher({ projects, selectedProjectId, onSelect, onCreate }: Props) {
  const [name, setName] = useState("Saturn Launch Plan");
  const [busy, setBusy] = useState(false);

  async function createProject() {
    if (!name.trim()) {
      return;
    }
    setBusy(true);
    try {
      await onCreate(name.trim());
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel project-switcher" aria-label="Projects">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Projects</p>
          <h2>Workspace</h2>
        </div>
        <span className="count-pill">{projects.length}</span>
      </div>
      <div className="project-list">
        {projects.map((project) => (
          <button
            type="button"
            key={project.id}
            className={project.id === selectedProjectId ? "project-item active" : "project-item"}
            onClick={() => onSelect(project.id)}
          >
            <span>{project.name}</span>
            <small>{project.status}</small>
          </button>
        ))}
      </div>
      <div className="inline-form">
        <input value={name} onChange={(event) => setName(event.target.value)} />
        <button type="button" onClick={createProject} disabled={busy}>
          {busy ? "Creating" : "New"}
        </button>
      </div>
    </section>
  );
}
