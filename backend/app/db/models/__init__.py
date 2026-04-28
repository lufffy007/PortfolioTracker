"""
SQLAlchemy models for the Portfolio Tracker domain.

Keep models focused on persistence concerns; domain logic should live
in services to remain reusable and suitable for AI agents.
"""

from app.db.session import Base

__all__ = ["Base"]

