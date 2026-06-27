# Security Architecture Decision Records (ADRs)

Track security-relevant architectural decisions.

## Format

```markdown
### ADR-00XX: Title

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded

**Context**: Why are we making this decision?

**Decision**: What did we decide?

**Consequences**: Trade-offs, risks, mitigations.
```

## Records

<!-- Add new ADRs above this line -->

### ADR-0001: Supabase RLS for Multi-Tenancy

**Date**: 2026-06-19
**Status**: Accepted

**Context**: We need to ensure users can only access their own portfolios and trades.

**Decision**: Use Supabase Row Level Security (RLS) policies enforced at the database layer.

**Consequences**: 
- Frontend/auth layer is not the sole security boundary.
- All queries must include `auth.uid()` checks.
- RLS policies live in `database/rls-policies/`.
