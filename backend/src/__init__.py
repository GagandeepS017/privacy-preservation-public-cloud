"""Application factory for the cloud authenticator backend."""
from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .auth import REVOKED_TOKENS, auth_bp
from .config import Config
from .database import init_db
from .face import face_bp
from .protected import api_bp


def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
    jwt = JWTManager(app)

    # --- JWT lifecycle handlers -----------------------------------------
    @jwt.token_in_blocklist_loader
    def _is_revoked(_header, payload) -> bool:
        return payload["jti"] in REVOKED_TOKENS

    @jwt.unauthorized_loader
    def _missing_token(reason):  # no Authorization header at all
        return jsonify(msg="Missing Authorization Header"), 401

    @jwt.invalid_token_loader
    def _invalid_token(reason):
        return jsonify(msg="Invalid token"), 422

    @jwt.expired_token_loader
    def _expired_token(_header, _payload):
        return jsonify(msg="Token has expired"), 401

    @jwt.revoked_token_loader
    def _revoked_token(_header, _payload):
        return jsonify(msg="Token has been revoked"), 401

    # --- Routes ----------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(face_bp)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", face_enabled=config.face_enabled()), 200

    with app.app_context():
        init_db()

    return app
