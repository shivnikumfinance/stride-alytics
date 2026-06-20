---
description: "StrideAlytics docs-first workflow — always consult the docs/ folder before implementing, planning, or reviewing technical or business requirements. Use when: working on features, architecture, business rules, financial model, application requirements, layer changes, or any task mentioning 'requirements', 'tech', 'business', 'architecture', or 'spec'."
applyTo: "**"
---

# StrideAlytics — Docs-First Requirement

**Authoritative documentation source:** `docs/` in the repository root.

## Mandatory Pre-Task Reading

For **every** task involving technical or business requirements, the agent MUST read the relevant docs **before** proposing code, plans, refactors, or answers.

## Trigger Conditions

Read the docs FIRST when the request mentions ANY of:
- "requirement(s)", "tech requirement", "business requirement"
- "feature", "implement", "build", "create", "add" (any feature work)
- "architecture", "design", "plan", "spec", "specification"
- "business rules", "financial model", "application requirements"
- "frontend", "backend", "mobile", "database", "scheduler", "deployment", "ci/cd"
- "trades", "portfolio", "analytics", "users" (domain entities)

## Reading Order (follow exactly)

### 1. Always read these first
- `docs/README.md` — documentation hub and role-based navigation
- `docs/TECHNICAL/00-ARCHITECTURE-INDEX.md` — technical nav hub

### 2. Then read based on task type

**Business / product / stakeholder tasks:**
- `docs/BUSINESS/01-BUSINESS-REQUIREMENTS.md`
- `docs/BUSINESS/02-BUSINESS-RULES.md`
- `docs/BUSINESS/03-FINANCIAL-MODEL.md`
- `docs/BUSINESS/04-APPLICATION-REQUIREMENTS.md`

**Technical / implementation tasks:**
- `docs/TECHNICAL/01-SYSTEM-OVERVIEW.md`
- `docs/TECHNICAL/02-SYSTEM-DIAGRAMS.md`
- `docs/TECHNICAL/03-FOLDER-STRUCTURE.md`
- `docs/TECHNICAL/BLUEPRINT.md`
- `docs/TECHNICAL/LAYERS/<matching-layer>.md`
- `docs/TECHNICAL/RULES/CODING-STANDARDS.md`
- `docs/TECHNICAL/RULES/FOLDER-CONVENTIONS.md`
- `docs/TECHNICAL/RULES/DATA-FLOW-RULES.md`
- `docs/TECHNICAL/REFERENCES/LIBRARIES-BY-LAYER.md`

**Phased planning tasks:**
- `docs/TECHNICAL/PHASES/IMPLEMENTATION-PHASES.md`
- `docs/TECHNICAL/PHASES/QUICK-START-CHECKLIST.md`
- `docs/TECHNICAL/PHASES/ROADMAP.md`

### 3. Reference docs as needed
- `docs/TECHNICAL/REFERENCES/INFRASTRUCTURE-OVERVIEW.md`
- `docs/TECHNICAL/SUPABASE-SETUP.md`

## Behavioral Rules

1. **Never invent specs.** If a doc defines a rule, field, endpoint, or constraint, cite the file path in your response.
2. **Cite, don't paraphrase silently.** When answering a requirement question, quote or summarize from the doc with a markdown link like `[01-BUSINESS-REQUIREMENTS](docs/BUSINESS/01-BUSINESS-REQUIREMENTS.md)`.
3. **Flag conflicts.** If the user's request conflicts with the docs, surface the conflict before proceeding.
4. **Layer routing.** Map the request to the correct layer doc in `docs/TECHNICAL/LAYERS/` before generating layer-specific code.
5. **Re-read on context loss.** If a long conversation has lost the docs context, re-read the relevant docs before continuing.

## Quick Layer → Doc Map

| Work Area | Read |
|-----------|------|
| React web app, Vite, Tremor | `docs/TECHNICAL/LAYERS/01-FRONTEND-LAYER.md` |
| React Native, Expo, NativeWind | `docs/TECHNICAL/LAYERS/02-MOBILE-LAYER.md` |
| FastAPI, Python API | `docs/TECHNICAL/LAYERS/03-BACKEND-LAYER.md` |
| Supabase, PostgreSQL, RLS, schema | `docs/TECHNICAL/LAYERS/04-DATABASE-LAYER.md` |
| GitHub Actions cron jobs | `docs/TECHNICAL/LAYERS/05-SCHEDULER-LAYER.md` |
| Vercel, Render, hosting | `docs/TECHNICAL/LAYERS/06-DEPLOYMENT-LAYER.md` |
| CI/CD pipelines | `docs/TECHNICAL/LAYERS/07-CI-CD-LAYER.md` |

## Documentation Locations

- Repository root: `docs/`
- Business: `docs/BUSINESS/`
- Technical: `docs/TECHNICAL/`
- If docs are missing a topic, ask the user before fabricating.
