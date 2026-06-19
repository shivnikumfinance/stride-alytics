# 🏗️ StrideAlytics — Architecture Documentation Index

**Navigation Hub for Complete System Architecture**

---

## 📋 Quick Links

### Core Architecture
- [**01-SYSTEM-OVERVIEW**](./01-SYSTEM-OVERVIEW.md) — System description, tech stack, key components
- [**02-SYSTEM-DIAGRAMS**](./02-SYSTEM-DIAGRAMS.md) — Visual representations (Mermaid + ASCII)
- [**03-FOLDER-STRUCTURE**](./03-FOLDER-STRUCTURE.md) — Complete monorepo directory tree

---

## 🔧 Architecture Layers

Each layer represents a distinct part of the system. Read them in sequence or jump to your layer.

| Layer | File | Purpose |
|-------|------|---------|
| 🎨 **Frontend** | [01-FRONTEND-LAYER](./LAYERS/01-FRONTEND-LAYER.md) | React + Vite + Tremor web application |
| 📱 **Mobile** | [02-MOBILE-LAYER](./LAYERS/02-MOBILE-LAYER.md) | React Native + Expo mobile application |
| ⚙️ **Backend** | [03-BACKEND-LAYER](./LAYERS/03-BACKEND-LAYER.md) | FastAPI Python backend services |
| 🗄️ **Database** | [04-DATABASE-LAYER](./LAYERS/04-DATABASE-LAYER.md) | Supabase PostgreSQL + auth |
| ⏰ **Scheduler** | [05-SCHEDULER-LAYER](./LAYERS/05-SCHEDULER-LAYER.md) | GitHub Actions CRON jobs |
| 🚀 **Deployment** | [06-DEPLOYMENT-LAYER](./LAYERS/06-DEPLOYMENT-LAYER.md) | Vercel, Render, Supabase infrastructure |
| 🔄 **CI/CD** | [07-CI-CD-LAYER](./LAYERS/07-CI-CD-LAYER.md) | Build pipelines, automated testing, deployment flows |

---

## 📚 References

Supporting documentation for tech stack, infrastructure, and configuration.

- [**LIBRARIES-BY-LAYER**](./REFERENCES/LIBRARIES-BY-LAYER.md) — Complete dependency breakdown by layer
- [**INFRASTRUCTURE-OVERVIEW**](./REFERENCES/INFRASTRUCTURE-OVERVIEW.md) — Services, hosts, and deployment targets

---

## 📏 Rules & Standards

Guidelines for consistent development across the project.

- [**CODING-STANDARDS**](./RULES/CODING-STANDARDS.md) — Code conventions, naming, best practices
- [**FOLDER-CONVENTIONS**](./RULES/FOLDER-CONVENTIONS.md) — Directory naming and organization rules
- [**DATA-FLOW-RULES**](./RULES/DATA-FLOW-RULES.md) — Request/response patterns and data contracts

---

## 🎯 How to Use This Documentation

### For New Team Members
1. Start with [01-SYSTEM-OVERVIEW](./01-SYSTEM-OVERVIEW.md)
2. Review [02-SYSTEM-DIAGRAMS](./02-SYSTEM-DIAGRAMS.md)
3. Read your assigned layer(s)
4. Review [RULES](./RULES/) folder for coding standards

### For Architecture Review
- [03-FOLDER-STRUCTURE](./03-FOLDER-STRUCTURE.md) — See all directories
- Layer-specific files for deep dives
- [INFRASTRUCTURE-OVERVIEW](./REFERENCES/INFRASTRUCTURE-OVERVIEW.md) — Deployment topology

### For Feature Implementation
1. Identify affected layer(s)
2. Read the relevant layer document
3. Check [LIBRARIES-BY-LAYER](./REFERENCES/LIBRARIES-BY-LAYER.md) for tech stack
4. Follow [RULES](./RULES/) for coding standards

### For Deployment Questions
- [06-DEPLOYMENT-LAYER](./LAYERS/06-DEPLOYMENT-LAYER.md) — Infrastructure setup
- [07-CI-CD-LAYER](./LAYERS/07-CI-CD-LAYER.md) — Build and deployment automation
- [INFRASTRUCTURE-OVERVIEW](./REFERENCES/INFRASTRUCTURE-OVERVIEW.md) — Service endpoints

---

## 📊 System at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    StrideAlytics Platform                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🎨 Frontend (React)        📱 Mobile (React Native)        │
│  ↓                           ↓                              │
│  └─────────────┬─────────────┘                             │
│                ▼                                             │
│         ⚙️ Backend API (FastAPI)                            │
│                ▼                                             │
│      🗄️ Database (Supabase PostgreSQL)                      │
│                ▼                                             │
│         ⏰ Schedulers (GitHub Actions)                       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Deployment: Vercel (Web) | Render (API) | Supabase (DB)   │
│  CI/CD: GitHub Actions | Automated Testing & Deployment    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 File Map

```
docs/
├── 00-ARCHITECTURE-INDEX.md              ← YOU ARE HERE
├── 01-SYSTEM-OVERVIEW.md
├── 02-SYSTEM-DIAGRAMS.md
├── 03-FOLDER-STRUCTURE.md
│
├── LAYERS/
│   ├── 01-FRONTEND-LAYER.md
│   ├── 02-MOBILE-LAYER.md
│   ├── 03-BACKEND-LAYER.md
│   ├── 04-DATABASE-LAYER.md
│   ├── 05-SCHEDULER-LAYER.md
│   ├── 06-DEPLOYMENT-LAYER.md
│   └── 07-CI-CD-LAYER.md
│
├── REFERENCES/
│   ├── LIBRARIES-BY-LAYER.md
│   └── INFRASTRUCTURE-OVERVIEW.md
│
└── RULES/
    ├── CODING-STANDARDS.md
    ├── FOLDER-CONVENTIONS.md
    └── DATA-FLOW-RULES.md
```

---

## 📝 Version Info

- **Project:** StrideAlytics
- **Platform:** Multi-platform analytics system (Web + Mobile + Backend)
- **Created:** 2026-06-15
- **Documentation Version:** A
- **Status:** Production-Ready Blueprint

---

## ❓ Need Help?

- **System Architecture?** → Start with [01-SYSTEM-OVERVIEW](./01-SYSTEM-OVERVIEW.md)
- **Specific Layer?** → Jump to [LAYERS/](./LAYERS/)
- **Tech Stack?** → See [LIBRARIES-BY-LAYER](./REFERENCES/LIBRARIES-BY-LAYER.md)
- **Deployment?** → Check [06-DEPLOYMENT-LAYER](./LAYERS/06-DEPLOYMENT-LAYER.md) + [07-CI-CD-LAYER](./LAYERS/07-CI-CD-LAYER.md)
- **Code Rules?** → Review [RULES/](./RULES/)

---

**Last Updated:** 2026-06-15
