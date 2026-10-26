import { useState } from "react";

const STORAGE_KEY = "monet.contributor";

function remembered(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

export function useContributor(): [string, (name: string) => void] {
  const [name, setName] = useState(remembered);
  const update = (next: string) => {
    setName(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      return;
    }
  };
  return [name, update];
}
