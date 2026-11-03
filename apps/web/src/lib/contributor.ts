import { useSyncExternalStore } from "react";

const listeners = new Set<() => void>();

function read(storageKey: string): string {
  try {
    return localStorage.getItem(storageKey) ?? "";
  } catch {
    return "";
  }
}

function write(storageKey: string, value: string): void {
  try {
    localStorage.setItem(storageKey, value);
  } catch {
    return;
  } finally {
    for (const listener of listeners) listener();
  }
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function useRemembered(storageKey: string): [string, (value: string) => void] {
  const value = useSyncExternalStore(
    subscribe,
    () => read(storageKey),
    () => "",
  );
  return [
    value,
    (next: string) => {
      write(storageKey, next);
    },
  ];
}

export function useContributor(): [string, (name: string) => void] {
  return useRemembered("monet.contributor");
}

export function useContributorEmail(): [string, (email: string) => void] {
  return useRemembered("monet.email");
}

export function credit(name: string | null, email: string | null): string | null {
  if (name !== null && email !== null) return `${name} (${email})`;
  return name ?? email;
}
