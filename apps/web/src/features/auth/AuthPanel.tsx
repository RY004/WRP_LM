"use client";

import { useState } from "react";

import type { ApiClient, SessionRead } from "../../lib/api";
import { storeSession } from "../../lib/auth";

type Props = {
  api: ApiClient;
  onSession: (token: string, session: SessionRead) => void;
};

export function AuthPanel({ api, onSession }: Props) {
  const [email, setEmail] = useState("builder@saturn.local");
  const [name, setName] = useState("Saturn Builder");
  const [orgSlug, setOrgSlug] = useState("saturn-workspace");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    try {
      const session = await api.login({
        email,
        name,
        org_slug: orgSlug,
        org_name: orgSlug.replace(/-/g, " "),
      });
      storeSession(session.session_id);
      onSession(session.session_id, session);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-panel" aria-label="Sign in">
      <div>
        <p className="eyebrow">Saturn Workspace</p>
        <h1>Project command center</h1>
        <p className="lede">
          Sign in to create a project, write artifacts, query project knowledge, manage Notion
          sync, and move pipeline work from one browser surface.
        </p>
      </div>
      <div className="auth-grid">
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          Name
          <input value={name} onChange={(event) => setName(event.target.value)} />
        </label>
        <label>
          Org slug
          <input value={orgSlug} onChange={(event) => setOrgSlug(event.target.value)} />
        </label>
        <button type="button" className="primary-action" onClick={submit} disabled={busy}>
          {busy ? "Signing in" : "Sign in"}
        </button>
      </div>
    </section>
  );
}
