import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const nextConfig = require("eslint-config-next/core-web-vitals");

export default [
  ...nextConfig,
  {
    files: ["**/*.ts", "**/*.tsx"],
    plugins: { "@typescript-eslint": tsPlugin },
    languageOptions: { parser: tsParser },
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "no-unused-vars": "off",
    },
  },
];
