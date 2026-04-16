"use client";

import { useEffect, useMemo, useState } from "react";

import { ArtifactWorkspace } from "../artifacts/ArtifactWorkspace";
import { AuthPanel } from "../auth/AuthPanel";
import { RagChatPanel } from "../chat/RagChatPanel";
import { NotionPanel } from "../notion/NotionPanel";
import { PipelinePanel } from "../pipeline/PipelinePanel";
import { ProjectSwitcher } from "../projects/ProjectSwitcher";
import { RetrievalPanel } from "../retrieval/RetrievalPanel";
import {
  ApiError,
  type ArtifactRead,
  createApiClient,
  type PipelineRead,
  type ProjectRead,
  type SessionRead,
} from "../../lib/api";
import { clearStoredSession, readStoredSession } from "../../lib/auth";

export function SaturnWorkbench() {
  const [token, setToken] = useState<string | null>(null);
  const [session, setSession] = useState<SessionRead | null>(null);
  const [projects, setProjects] = useState<ProjectRead[]>([]);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [pipeline, setPipeline] = useState<PipelineRead | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactRead[]>([]);
  const [lastRetrievedAnswer, setLastRetrievedAnswer] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const api = useMemo(() => createApiClient(token), [token]);

  useEffect(() => {
    const stored = readStoredSession();
    if (stored) {
      setToken(stored);
    }
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }
    void bootstrap();
  }, [token]);

  useEffect(() => {
    if (!projectId || !token) {
      setPipeline(null);
      setArtifacts([]);
      return;
    }
    void refreshProject(projectId);
  }, [projectId, token]);

  async function capture<T>(task: () => Promise<T>): Promise<T | null> {
    setError(null);
    try {
      return await task();
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(`${caught.status}: ${JSON.stringify(caught.detail)}`);
      } else if (caught instanceof Error) {
        setError(caught.message);
      } else {
        setError("Unexpected Saturn web error");
      }
      return null;
    }
  }

  async function bootstrap() {
    setLoading(true);
    try {
      await capture(async () => {
        const [nextSession, nextProjects] = await Promise.all([api.session(), api.listProjects()]);
        setSession(nextSession);
        setProjects(nextProjects);
        setProjectId((current) => current ?? nextProjects[0]?.id ?? null);
      });
    } finally {
      setLoading(false);
    }
  }

  async function refreshProject(nextProjectId = projectId) {
    if (!nextProjectId) {
      return;
    }
    await capture(async () => {
      const [nextPipeline, nextArtifacts] = await Promise.all([
        api.getPipeline(nextProjectId),
        api.listArtifacts(nextProjectId),
      ]);
      setPipeline(nextPipeline);
      setArtifacts(nextArtifacts);
    });
  }

  async function createProject(name: string) {
    const project = await capture(() => api.createProject(name));
    if (project) {
      setProjects((current) => [project, ...current.filter((item) => item.id !== project.id)]);
      setProjectId(project.id);
    }
  }

  function onSession(nextToken: string, nextSession: SessionRead) {
    setToken(nextToken);
    setSession(nextSession);
  }

  function signOut() {
    clearStoredSession();
    setToken(null);
    setSession(null);
    setProjects([]);
    setProjectId(null);
    setPipeline(null);
    setArtifacts([]);
  }

  if (!token || !session) {
    return (
      <main className="app-shell auth-shell">
        {error ? <div className="error-banner">{error}</div> : null}
        <AuthPanel api={api} onSession={onSession} />
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <strong>Saturn</strong>
            <small>{session.user.email}</small>
          </div>
        </div>
        <div className="topbar-actions">
          {loading ? <span className="status-chip">Loading</span> : null}
          <button type="button" onClick={signOut}>
            Sign out
          </button>
        </div>
      </header>
      {error ? <div className="error-banner">{error}</div> : null}
      <div className="workspace-grid">
        <ProjectSwitcher
          projects={projects}
          selectedProjectId={projectId}
          onSelect={setProjectId}
          onCreate={createProject}
        />
        <PipelinePanel
          api={api}
          projectId={projectId}
          pipeline={pipeline}
          onRefresh={() => refreshProject()}
        />
        <ArtifactWorkspace
          api={api}
          projectId={projectId}
          artifacts={artifacts}
          onRefresh={() => refreshProject()}
        />
        <RetrievalPanel api={api} projectId={projectId} onAnswer={setLastRetrievedAnswer} />
        <NotionPanel api={api} projectId={projectId} />
        <RagChatPanel api={api} projectId={projectId} lastRetrievedAnswer={lastRetrievedAnswer} />
      </div>
    </main>
  );
}
