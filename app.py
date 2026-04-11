"""Vercel Flask entrypoint.

Exports the Flask app instance for Vercel's Python runtime discovery.
"""

import os

from backend.app import app


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	host = os.environ.get("HOST", "0.0.0.0")
	app.run(host=host, port=port)
