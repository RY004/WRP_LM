export const sessionCookieName = "saturn_session";
export const sessionStorageKey = "saturn.session";

export function readStoredSession(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(sessionStorageKey);
}

export function storeSession(token: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(sessionStorageKey, token);
  document.cookie = `${sessionCookieName}=${encodeURIComponent(token)}; path=/; SameSite=Lax`;
}

export function clearStoredSession(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(sessionStorageKey);
  document.cookie = `${sessionCookieName}=; path=/; max-age=0; SameSite=Lax`;
}
