import type { ArtifactRead } from "./api";

function safeFileName(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || "artifact";
}

export function downloadArtifactMarkdown(artifact: ArtifactRead): void {
  const blob = new Blob([artifact.rendered_markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${safeFileName(artifact.title)}.md`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function downloadBulkMarkdown(artifacts: ArtifactRead[]): void {
  const payload = artifacts
    .map((artifact) => `# ${artifact.title}\n\n${artifact.rendered_markdown}`)
    .join("\n\n---\n\n");
  const blob = new Blob([payload], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "saturn-artifacts-export.md";
  anchor.click();
  URL.revokeObjectURL(url);
}
