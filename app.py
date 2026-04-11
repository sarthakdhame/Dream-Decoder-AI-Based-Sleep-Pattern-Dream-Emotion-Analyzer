"""
Dream Decoder - Main Flask Application
Production entrypoint for Vercel/Render deployment
"""
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from backend.config import DEBUG, CORS_ORIGINS
from backend.database.db import init_db
from backend.routes import dreams_bp, sleep_bp, analysis_bp, insights_bp
from backend.routes.auth import auth_bp


# Create and configure Flask app
app = Flask(__name__, static_folder="frontend", static_url_path="")

# Enable CORS with production origins
CORS(app, origins=CORS_ORIGINS)

# Initialize database
init_db()

# Register API blueprints
app.register_blueprint(auth_bp)      # Authentication routes
app.register_blueprint(dreams_bp)    # Dream management
app.register_blueprint(sleep_bp)     # Sleep tracking
app.register_blueprint(analysis_bp)  # Dream analysis
app.register_blueprint(insights_bp)  # Insights generation

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Dream Decoder API is running!'
    })

# Serve frontend
@app.route('/')
def serve_index():
    """Serve the main HTML page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    import traceback
    print("DEBUG: Internal Server Error")
    traceback.print_exc()
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
