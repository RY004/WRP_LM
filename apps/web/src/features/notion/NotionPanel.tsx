"use client";

import { useEffect, useState } from "react";

import type {
  ApiClient,
  NotionAccountRead,
  NotionResourceRead,
  NotionSyncTargetRead,
} from "../../lib/api";

type Props = {
  api: ApiClient;
  projectId: string | null;
};

export function NotionPanel({ api, projectId }: Props) {
  const [accounts, setAccounts] = useState<NotionAccountRead[]>([]);
  const [resources, setResources] = useState<NotionResourceRead[]>([]);
  const [targets, setTargets] = useState<NotionSyncTargetRead[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<string>("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void refresh();
  }, [projectId]);

  async function refresh() {
    const [nextAccounts, nextTargets] = await Promise.all([
      api.listNotionAccounts().catch(() => []),
      projectId ? api.listNotionTargets(projectId).catch(() => []) : Promise.resolve([]),
    ]);
    setAccounts(nextAccounts);
    setTargets(nextTargets);
    const accountId = selectedAccount || nextAccounts[0]?.id || "";
    setSelectedAccount(accountId);
    if (accountId) {
      setResources(await api.listNotionResources(accountId).catch(() => []));
    }
  }

  async function connectTestWorkspace() {
    setBusy(true);
    try {
      const start = await api.startNotionOAuth();
      const account = await api.completeNotionOAuth("web-phase8", start.state);
      setAccounts((current) => [account, ...current.filter((item) => item.id !== account.id)]);
      setSelectedAccount(account.id);
      setResources(await api.listNotionResources(account.id));
    } finally {
      setBusy(false);
    }
  }

  async function addTarget(resource: NotionResourceRead) {
    if (!projectId || !selectedAccount) {
      return;
    }
    await api.createNotionTarget({
      account_id: selectedAccount,
      project_id: projectId,
      notion_resource_id: resource.id,
      resource_type: resource.resource_type,
      title: resource.title,
    });
    await refresh();
  }

  async function syncTarget(targetId: string) {
    await api.triggerNotionSync(targetId);
    await refresh();
  }

  return (
    <section className="panel notion-panel" aria-label="Notion sync">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Notion</p>
          <h2>Sync targets</h2>
        </div>
        <button type="button" onClick={connectTestWorkspace} disabled={busy}>
          {busy ? "Connecting" : "Connect"}
        </button>
      </div>
      <select value={selectedAccount} onChange={(event) => setSelectedAccount(event.target.value)}>
        <option value="">No account</option>
        {accounts.map((account) => (
          <option key={account.id} value={account.id}>
            {account.workspace_name}
          </option>
        ))}
      </select>
      <div className="split-list">
        <div>
          <h3>Resources</h3>
          <div className="compact-list">
            {resources.map((resource) => (
              <button type="button" key={resource.id} onClick={() => addTarget(resource)}>
                {resource.title}
              </button>
            ))}
          </div>
        </div>
        <div>
          <h3>Targets</h3>
          <div className="compact-list">
            {targets.map((target) => (
              <button type="button" key={target.id} onClick={() => syncTarget(target.id)}>
                {target.title} / {target.status}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
