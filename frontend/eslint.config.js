// ESLint v9 flat config for the StrideAlytics frontend.
//
// Plugins installed (see package.json devDependencies):
//   - eslint                       ^9.21.0
//   - @eslint/js                   ^9.21.0  (recommended ruleset)
//   - typescript-eslint            ^8.18.1  (meta-package: parser + plugin + configs)
//   - eslint-plugin-react          ^7.37.4  (legacy plugin — bridged via FlatCompat)
//   - eslint-plugin-react-hooks    ^5.1.0
//   - eslint-plugin-react-refresh  ^0.4.19
//
// Run via: `npm run lint` (or `npm run verify`).
// See docs/TECHNICAL/RULES/frontend/FRONTEND-CODING-STANDARDS.md.

import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactPlugin from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import { FlatCompat } from "@eslint/eslintrc";

const compat = new FlatCompat({ baseDirectory: import.meta.dirname });

export default [
  // 1. Base recommended ruleset for all JS files
  js.configs.recommended,

  // 2. Project-wide ignores
  {
    ignores: [
      "dist/**",
      ".vite/**",
      "node_modules/**",
      "coverage/**",
      "**/*.d.ts",
    ],
  },

  // 3. TypeScript — apply recommended rules to TS/TSX
  ...tseslint.configs.recommended.map((c) => ({
    ...c,
    files: ["**/*.{ts,tsx}"],
  })),

  // 4. React + React Hooks + React Refresh (FlatCompat bridges eslint-plugin-react v7)
  ...compat.extends("plugin:react/recommended", "plugin:react/jsx-runtime"),
  {
    files: ["**/*.{ts,tsx,jsx,js}"],
    plugins: {
      react: reactPlugin,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    languageOptions: {
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: { version: "detect" },
    },
    rules: {
      // React 19 + new JSX transform — no need to import React in every file
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",

      // Hooks
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      // Vite HMR — components must be stable across reloads
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],

      // TypeScript — relax a few noisy defaults
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/consistent-type-imports": [
        "warn",
        { prefer: "type-imports", fixStyle: "separate-type-imports" },
      ],
      "@typescript-eslint/no-empty-object-type": "warn",

      // General hygiene
      "no-console": ["warn", { allow: ["warn", "error", "info"] }],
      eqeqeq: ["error", "always", { null: "ignore" }],
      "prefer-const": "warn",
      "no-var": "error",
    },
  },

  // 5. Test files get a slightly looser rule set (React Refresh + some
  //    type rules are noise there)
  {
    files: ["**/*.test.{ts,tsx}", "**/__tests__/**", "src/test/**"],
    rules: {
      "react-refresh/only-export-components": "off",
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
];
