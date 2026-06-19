## Summary

<!-- One-paragraph description of the change. -->

## Linked issues

<!-- Use "Closes #123" or "Refs #123" so GitHub auto-links. -->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that breaks existing behavior)
- [ ] Documentation / infra only

## How was this tested?

- [ ] Backend: `uv run pytest` passes
- [ ] Backend: `uv run python -c "from app.main import app"` succeeds
- [ ] Frontend: `npm run build` succeeds
- [ ] Manual: `curl` against local uvicorn (paste responses below)
- [ ] Database: `sqlfluff lint database/**/*.sql` clean

## Screenshots / curl output

```bash
# paste relevant requests / responses
```

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have added tests that prove my fix / feature works
- [ ] New and existing unit tests pass locally
- [ ] I have updated relevant documentation
- [ ] I have added a changeset / changelog entry (if applicable)
- [ ] No new secrets were committed
