"""
Dream Decoder - Flask Application
Main entry point for the backend server
"""
import os
import sys
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env and let local edits win during development.
load_dotenv(override=True)

from backend.config import DEBUG, HOST, PORT, CORS_ORIGINS
from backend.database.db import init_db
from backend.routes import dreams_bp, sleep_bp, analysis_bp, insights_bp
from backend.routes.auth import auth_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Enable CORS with explicit resources and credentials support for preflight requests.
    CORS(
        app,
        resources={r"/*": {"origins": CORS_ORIGINS}},
        supports_credentials=True,
        allow_headers='*',
        expose_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'],
        always_send=True
    )

    def _normalize_origin(value):
        """Normalize origin strings for reliable matching."""
        if not isinstance(value, str):
            return ''
        return value.strip().strip('"').strip("'").rstrip('/').lower()

    def _origin_allowed(origin):
        """Check whether request origin is allowed by configured CORS origins."""
        origin_norm = _normalize_origin(origin)
        if not origin_norm:
            return False

        if CORS_ORIGINS == '*':
            return True

        for allowed in CORS_ORIGINS:
            allowed_norm = _normalize_origin(allowed)
            if not allowed_norm:
                continue

            if allowed_norm == origin_norm:
                return True

            # Support regex-style origin entries configured in CORS_ORIGINS.
            if any(ch in allowed for ch in ['*', '\\', '.', '^', '$', '?', '+', '[', ']', '(', ')', '|']):
                try:
                    if re.fullmatch(allowed, origin_norm):
                        return True
                except re.error:
                    continue

        # Safety fallback for current deployment domains.
        if origin_norm.endswith('.vercel.app') or origin_norm.endswith('.onrender.com'):
            return True

        return False
    
    # Initialize database
    init_db()
    
    # Register blueprints (API routes)
    app.register_blueprint(auth_bp)  # Authentication routes
    app.register_blueprint(dreams_bp)
    app.register_blueprint(sleep_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(insights_bp)
    
    # Serve frontend
    @app.route('/')
    def serve_frontend():
        """Serve the main HTML page."""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files."""
        return send_from_directory(app.static_folder, path)
    
    # Cache control for static assets
    @app.after_request
    def add_header(response):
        """Add headers to both force latest IE rendering engine or to cache static assets."""
        origin = request.headers.get('Origin')
        if _origin_allowed(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Vary'] = 'Origin'

            # Ensure browser preflight requests always receive allowed headers/methods.
            requested_headers = request.headers.get('Access-Control-Request-Headers')
            if requested_headers:
                response.headers['Access-Control-Allow-Headers'] = requested_headers
            else:
                response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'

            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'

        if 'Cache-Control' not in response.headers:
            # Cache static assets for 1 day
            if request.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
                response.headers['Cache-Control'] = 'public, max-age=86400'
        return response

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'message': 'Dream Decoder API is running!'
        })
    
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
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    # Get port from environment variable with fallback to 5000
    port = int(os.environ.get("PORT", 5000))
    
    print("=" * 60)
    print("Dream Decoder - Starting Server")
    print("=" * 60)
    
    # Optionally preload models (comment out for faster startup during dev)
    # from backend.services.nlp_engine import preload_models
    # preload_models()
    
    print(f"\nServer running at http://0.0.0.0:{port}")
    
    # Verify Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        # Check if it's the placeholder from .env.example
        if gemini_key == "your_gemini_api_key_here":
            print("WARNING: GEMINI_API_KEY is still set to placeholder! Please update your .env file.")
        else:
            print(f"OK: GEMINI API KEY DETECTED ({gemini_key[:4]}...{gemini_key[-4:]})")
    else:
        print("WARNING: GEMINI_API_KEY NOT FOUND IN ENVIRONMENT")
        
    print("Press Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
