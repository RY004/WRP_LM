import { expect, test } from "@playwright/test";

test("renders the signed-out product workflow entry", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Project command center" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
  await expect(page.getByLabel("Email")).toHaveValue("builder@saturn.local");
});

test("exposes project workspace panels with a browser session", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("saturn.session", "browser-session");
  });
  await page.route("**/api/v1/session", async (route) => {
    await route.fulfill({
      json: {
        session_id: "browser-session",
        org_id: "org-1",
        user: { id: "user-1", email: "builder@saturn.local", display_name: "Builder" },
      },
    });
  });
  await page.route("**/api/v1/projects", async (route) => {
    await route.fulfill({
      json: [{ id: "project-1", org_id: "org-1", name: "Saturn Launch", slug: "saturn-launch", status: "active" }],
    });
  });
  await page.route("**/api/v1/pipeline/projects/project-1", async (route) => {
    await route.fulfill({
      json: {
        id: "pipe-1",
        project_id: "project-1",
        current_stage: "implement",
        cycle: 1,
        status: "active",
        branch_name: "main",
      },
    });
  });
  await page.route("**/api/v1/artifacts?project_id=project-1", async (route) => {
    await route.fulfill({ json: [] });
  });
  await page.route("**/api/v1/notion/accounts", async (route) => {
    await route.fulfill({ json: [] });
  });
  await page.route("**/api/v1/notion/projects/project-1/targets", async (route) => {
    await route.fulfill({ json: [] });
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Workspace" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "implement" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Authoring" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Project search" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Sync targets" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "RAG assistant" })).toBeVisible();
});
