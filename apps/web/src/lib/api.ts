export const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type SessionRead = {
  session_id: string;
  org_id: string;
  user: { id: string; email: string; display_name: string | null };
};

export type ProjectRead = {
  id: string;
  org_id: string;
  name: string;
  slug: string;
  status: string;
};

export type PipelineRead = {
  id: string;
  project_id: string;
  current_stage: string;
  cycle: number;
  status: string;
  branch_name: string;
};

export type ArtifactRead = {
  id: string;
  project_id: string;
  slug: string;
  title: string;
  artifact_type: string;
  status: string;
  current_version_number: number;
  normalized_content: Record<string, unknown>;
  rendered_markdown: string;
  index_projection: Record<string, unknown>;
};

export type ArtifactVersionRead = {
  id: string;
  artifact_id: string;
  version_number: number;
  rendered_markdown: string;
  change_summary: string | null;
};

export type ArtifactCommentRead = {
  id: string;
  artifact_id: string;
  version_id: string | null;
  body: string;
  status: string;
  created_by_user_id: string;
};

export type RetrievalMode = "unfiltered" | "strict_section" | "heading_boosted";

export type RetrievalResponse = {
  query: string;
  mode: RetrievalMode;
  degraded: boolean;
  diagnostics: string[];
  results: Array<{
    source_type: string;
    source_id: string;
    title: string;
    text: string;
    score: number;
    confidence: string;
    citation: {
      source_type: string;
      source_id: string;
      title: string;
      heading_path_text: string | null;
      section_path: string | null;
    };
  }>;
};

export type NotionAccountRead = {
  id: string;
  workspace_name: string;
  status: string;
  reconnect_reason: string | null;
};

export type NotionResourceRead = {
  id: string;
  resource_type: "page" | "database";
  title: string;
  updated_cursor: string | null;
};

export type NotionSyncTargetRead = {
  id: string;
  account_id: string;
  project_id: string;
  notion_resource_id: string;
  resource_type: string;
  title: string;
  status: string;
  cursor: string | null;
  document_id: string | null;
  last_error: string | null;
};

export type ApiClient = ReturnType<typeof createApiClient>;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detail: unknown,
  ) {
    super(message);
  }
}

type RequestOptions = RequestInit & {
  token?: string | null;
  idempotencyKey?: string;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (options.token) {
    headers.set("X-Saturn-Session-Id", options.token);
  }
  if (options.idempotencyKey) {
    headers.set("Idempotency-Key", options.idempotencyKey);
  }
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    let detail: unknown = response.statusText;
    try {
      detail = await response.json();
    } catch {
      detail = await response.text();
    }
    throw new ApiError(`Saturn API request failed: ${path}`, response.status, detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export function createApiClient(token: string | null) {
  return {
    login: (payload: { email: string; name: string; org_slug: string; org_name?: string }) =>
      request<SessionRead>("/api/v1/auth/google/callback", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    session: () => request<SessionRead>("/api/v1/session", { token }),
    listProjects: () => request<ProjectRead[]>("/api/v1/projects", { token }),
    createProject: (name: string) =>
      request<ProjectRead>("/api/v1/projects", {
        method: "POST",
        token,
        idempotencyKey: `web-project-${name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
        body: JSON.stringify({ name }),
      }),
    getPipeline: (projectId: string) =>
      request<PipelineRead>(`/api/v1/pipeline/projects/${projectId}`, { token }),
    advancePipeline: (projectId: string, override = false) =>
      request<PipelineRead>(`/api/v1/pipeline/projects/${projectId}/advance`, {
        method: "POST",
        token,
        body: JSON.stringify({ override }),
      }),
    approvePipeline: (projectId: string, note: string) =>
      request<{ id: string }>(`/api/v1/pipeline/projects/${projectId}/approve`, {
        method: "POST",
        token,
        body: JSON.stringify({ note }),
      }),
    rejectPipeline: (projectId: string, note: string) =>
      request<{ id: string }>(`/api/v1/pipeline/projects/${projectId}/reject`, {
        method: "POST",
        token,
        body: JSON.stringify({ note }),
      }),
    handoffPacket: (projectId: string) =>
      request<Record<string, unknown>>(`/api/v1/pipeline/projects/${projectId}/handoff`, { token }),
    listArtifacts: (projectId: string) =>
      request<ArtifactRead[]>(`/api/v1/artifacts?project_id=${encodeURIComponent(projectId)}`, {
        token,
      }),
    createArtifact: (payload: {
      project_id: string;
      title: string;
      artifact_type: string;
      markdown: string;
      stage?: string;
    }) =>
      request<ArtifactRead>("/api/v1/artifacts", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
      }),
    updateArtifact: (
      artifactId: string,
      payload: { title?: string; status?: string; markdown?: string; change_summary?: string },
    ) =>
      request<ArtifactRead>(`/api/v1/artifacts/${artifactId}`, {
        method: "PATCH",
        token,
        body: JSON.stringify(payload),
      }),
    listVersions: (artifactId: string) =>
      request<ArtifactVersionRead[]>(`/api/v1/artifacts/${artifactId}/versions`, { token }),
    listComments: (artifactId: string) =>
      request<ArtifactCommentRead[]>(`/api/v1/comments/artifacts/${artifactId}`, { token }),
    addComment: (artifactId: string, body: string) =>
      request<ArtifactCommentRead>(`/api/v1/comments/artifacts/${artifactId}`, {
        method: "POST",
        token,
        body: JSON.stringify({ body }),
      }),
    queryRetrieval: (payload: {
      project_id: string;
      query: string;
      mode: RetrievalMode;
      section_path_prefix?: string;
      include_documents?: boolean;
      include_artifacts?: boolean;
      limit?: number;
    }) =>
      request<RetrievalResponse>("/api/v1/retrieval/query", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
      }),
    listNotionAccounts: () => request<NotionAccountRead[]>("/api/v1/notion/accounts", { token }),
    startNotionOAuth: () =>
      request<{ authorization_url: string; state: string }>("/api/v1/notion/oauth/start", {
        method: "POST",
        token,
      }),
    completeNotionOAuth: (code: string, state: string) =>
      request<NotionAccountRead>("/api/v1/notion/oauth/callback", {
        method: "POST",
        token,
        body: JSON.stringify({ code, state }),
      }),
    listNotionResources: (accountId: string) =>
      request<NotionResourceRead[]>(`/api/v1/notion/accounts/${accountId}/resources`, { token }),
    listNotionTargets: (projectId: string) =>
      request<NotionSyncTargetRead[]>(
        `/api/v1/notion/projects/${encodeURIComponent(projectId)}/targets`,
        { token },
      ),
    createNotionTarget: (payload: {
      account_id: string;
      project_id: string;
      notion_resource_id: string;
      resource_type: "page" | "database";
      title: string;
    }) =>
      request<NotionSyncTargetRead>("/api/v1/notion/targets", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
      }),
    triggerNotionSync: (targetId: string) =>
      request<{ id: string; status: string; queue_name: string }>(
        `/api/v1/notion/targets/${targetId}/sync`,
        {
          method: "POST",
          token,
        },
      ),
  };
}
