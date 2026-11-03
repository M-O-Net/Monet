import { useSyncExternalStore } from "react";

const STORAGE_KEY = "monet.editorKey";
const listeners = new Set<() => void>();

export function readEditorKey(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

export function writeEditorKey(key: string): void {
  try {
    if (key === "") localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, key);
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

export function useEditorKey(): string {
  return useSyncExternalStore(subscribe, readEditorKey, () => "");
}
