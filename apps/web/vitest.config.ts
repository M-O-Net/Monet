import { defineConfig } from "vitest/config";

// Deliberately not sharing vite.config.ts: the only thing under test is a pure function, so
// there is no reason to run the router codegen plugin or build any React. Node environment for
// the same reason — KaTeX renders to a string and never touches the DOM.
export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
