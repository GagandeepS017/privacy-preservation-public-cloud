"""Authentication routes: register, login (token issue), logout."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash

from . import database as db

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

# In-memory set of revoked token IDs (jti). A real deployment would use Redis or
# a database table; for a single-process demo an in-memory set is enough to make
# logout genuinely invalidate a token server-side.
REVOKED_TOKENS: set[str] = set()


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or "").strip() or None

    if not email or not password:
        return jsonify(msg="email and password are required"), 400
    if db.get_user_by_email(email):
        return jsonify(msg="a user with that email already exists"), 409

    user_id = db.create_user(email, password, display_name)
    return jsonify(msg="user registered", id=user_id), 201


@auth_bp.post("/token")
def create_token():
    """Validate credentials and hand back a signed JWT access token."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify(msg="Bad email or password"), 401

    access_token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"email": user["email"], "name": user["display_name"]},
    )
    return jsonify(access_token=access_token), 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """Revoke the current token so it can no longer be used."""
    REVOKED_TOKENS.add(get_jwt()["jti"])
    return jsonify(msg="logged out"), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the profile of the currently authenticated user."""
    user = db.get_user_by_id(int(get_jwt_identity()))
    if not user:
        return jsonify(msg="user not found"), 404
    return jsonify(id=user["id"], email=user["email"], name=user["display_name"]), 200
