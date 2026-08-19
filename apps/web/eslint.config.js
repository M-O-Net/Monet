import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import { globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

export default tseslint.config(
  globalIgnores(["dist", "src/routeTree.gen.ts", "src/client/schema.d.ts"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      ...tseslint.configs.strictTypeChecked,
      ...tseslint.configs.stylisticTypeChecked,
    ],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      "react-hooks": reactHooks,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
    },
  },
);
