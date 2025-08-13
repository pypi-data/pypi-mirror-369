"""
Route package initializer.

This module exposes commonly used route modules so they can be imported
directly from :mod:`server.routes`.  Tests rely on being able to access
these modules via attribute access, e.g. ``from server.routes import planner``.
"""

from __future__ import annotations

from . import planner, terminal, test_runner

__all__ = ["planner", "terminal", "test_runner"]
