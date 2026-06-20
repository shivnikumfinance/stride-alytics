#!/usr/bin/env node
/**
 * Scan tracked files for high-entropy strings that look like real secrets.
 * Warns (does not block) on suspicion. Catches the most common case
 * where someone accidentally commits a real API key.
 */
import { execSync } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

// Patterns that ALWAYS indicate a secret (not just a placeholder).
const patterns = [
  { name: "Supabase service_role JWT",   regex: /eyJ[A-Za-z0-9_-]{40,}\.[A-Za-z0-9_-]{40,}\.[A-Za-z0-9_-]{20,}/g, block: true },
  { name: "SendGrid key",                regex: /SG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}/g, block: true },
  { name: "Slack webhook",               regex: /https:\/\/hooks\.slack\.com\/services\/[A-Z0-9/]{20,}/g, block: true },
  { name: "Vercel token",                regex: /vercel\.com\/api\/v\d+\/.+["'][A-Za-z0-9]{24,}["']/g, block: false },
  { name: "Supabase project password",   regex: /postgres:\/\/postgres:[^@]{8,}@db\.[a-z]+\.supabase\.co/g, block: true },
];

// 1) Find candidate files (tracked, non-binary, < 1MB)
let files;
try {
  files = execSync("git ls-files", { cwd: root, encoding: "utf8" })
    .split("\n")
    .filter(Boolean);
} catch {
  console.error("✗ Not a git repository (or git is not installed)");
  process.exit(2);
}

// 2) Skip these paths
const skipDirs = ["secrets/", "node_modules/", "dist/", "build/", ".venv/", "venv/"];
files = files.filter((f) => !skipDirs.some((d) => f.startsWith(d)));

let leaks = 0;
for (const f of files) {
  const full = path.join(root, f);
  if (!existsSync(full)) continue;
  let content;
  try {
    content = readFileSync(full, "utf8");
  } catch { continue; }
  if (content.length > 1_000_000) continue;

  for (const { name, regex, block } of patterns) {
    const matches = content.match(regex);
    if (matches && matches.length > 0) {
      console.error(`✗ Potential ${name} leak in ${f}: ${matches.length} match(es)`);
      leaks += matches.length;
      if (block) {
        console.error("  → this pattern is BLOCKED. Move to secrets/.");
      }
    }
  }
}

if (leaks > 0) {
  console.error(`\n${leaks} potential secret(s) found. See secrets/README.md.`);
  process.exit(1);
} else {
  console.log("✓ No secrets detected in tracked files.");
}
