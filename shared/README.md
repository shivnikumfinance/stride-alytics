# StrideAlytics — Shared Types, Schemas & Constants

Shared TypeScript types, Zod validation schemas, and constants used across both the web frontend and mobile app.

## Structure

```
shared/
├── types/          # TypeScript type definitions
│   ├── index.ts
│   ├── api.types.ts
│   ├── models.types.ts
│   ├── database.types.ts
│   └── enums.ts
├── schemas/        # Zod validation schemas
│   ├── index.ts
│   ├── user.schema.ts
│   ├── option.schema.ts
│   ├── portfolio.schema.ts
│   └── trade.schema.ts
├── constants/      # Shared constants
│   ├── api.constants.ts
│   └── ui.constants.ts
└── README.md