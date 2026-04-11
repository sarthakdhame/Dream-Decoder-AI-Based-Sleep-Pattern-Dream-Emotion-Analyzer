"""Vercel Flask entrypoint.

Exports the Flask app instance for Vercel's Python runtime discovery.
"""

from backend.app import app
