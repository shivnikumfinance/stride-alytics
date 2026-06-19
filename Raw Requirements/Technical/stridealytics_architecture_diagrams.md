# StrideAlytics — Architecture Diagrams  
Combined system, folder, and deployment flow diagrams.

---

# 1. System Architecture Diagram (High‑Level)

Frontend (Vercel)
        ↓
Backend API (Render)
        ↓
Database (Supabase)
        ↓
Schedulers (GitHub Actions)

This diagram shows the high‑level flow of data and services across the StrideAlytics platform.

---

# 2. Monorepo Folder Structure Diagram

optionstride/
 ├── frontend/
 ├── backend/
 ├── database/
 ├── scheduler/
 ├── shared/
 └── infra/

This diagram shows the top‑level structure of the monorepo and how each major subsystem is organized.

---

# 3. Deployment Flow Diagram (CI/CD)

GitHub Push
   ↓
Vercel Deploy (frontend)
Render Deploy (backend)
Supabase Migrations
GitHub Actions CRON

This diagram shows how code moves from GitHub to production across all services.

---

# END OF DIAGRAMS
