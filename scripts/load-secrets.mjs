#!/usr/bin/env node
/**
 * Cross-platform wrapper that prefers PowerShell on Windows and bash elsewhere.
 * Usage: node scripts/load-secrets.mjs <env>
 */
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const env = process.argv[2] || "local";
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

const isWin = process.platform === "win32";
const ps1 = path.join(root, "scripts", "load-secrets.ps1");
const sh  = path.join(root, "scripts", "load-secrets.sh");

let cmd, args;
if (isWin) {
  if (!existsSync(ps1)) { console.error(`✗ Missing ${ps1}`); process.exit(1); }
  cmd = "powershell";
  args = ["-ExecutionPolicy", "Bypass", "-File", ps1, "-Env", env];
} else {
  if (!existsSync(sh))  { console.error(`✗ Missing ${sh}`);  process.exit(1); }
  cmd = "bash";
  args = [sh, env];
}

const child = spawn(cmd, args, { stdio: "inherit" });
child.on("exit", (code) => process.exit(code ?? 0));
