"""Protected resource routes - these require a valid access token.

This mirrors the report's core idea: the *cloud* resources can only be reached
by presenting a token stamped by our authenticator. No token -> 401. Someone
else's file -> 403. Valid & authorized -> 200.
"""
from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from . import database as db

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/hello")
@jwt_required()
def hello():
    """The canonical protected endpoint from the report (Fig 9.3)."""
    name = get_jwt().get("email", "user")
    return jsonify(message=f"{name} is successfully logged in for cloud access."), 200


@api_bp.get("/files")
@jwt_required()
def files():
    """List the cloud files owned by the authenticated user."""
    owner_id = int(get_jwt_identity())
    return jsonify(files=db.list_files(owner_id)), 200


@api_bp.get("/files/<int:file_id>")
@jwt_required()
def read_file(file_id: int):
    """Read one file, enforcing ownership (403 for someone else's file)."""
    owner_id = int(get_jwt_identity())
    record = db.get_file(file_id)
    if not record:
        return jsonify(msg="file not found"), 404
    if record["owner_id"] != owner_id:
        return jsonify(msg="you do not have access to this file"), 403
    return jsonify(id=record["id"], name=record["name"], content=record["content"]), 200
