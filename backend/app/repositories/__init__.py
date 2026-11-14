"""Data-access layer. Endpoints talk to ``Repo``; nothing outside this package touches SQL."""

from app.repositories.sql import Repo

__all__ = ["Repo"]
