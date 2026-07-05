"""Optional biometric layer - a thin proxy to Exadel CompreFace.

The report adds a second factor: a face-verification token that is concatenated
with the password-based JWT to raise the security bar. CompreFace is a heavy
Dockerised service, so this layer is *optional*: if it is not configured the
endpoint reports that clearly and the rest of the app keeps working.

CompreFace docs: https://github.com/exadel-inc/CompreFace
"""
from __future__ import annotations

import base64
import binascii

import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .config import Config

face_bp = Blueprint("face", __name__, url_prefix="/api/face")


@face_bp.get("/status")
def status():
    return jsonify(
        enabled=Config.face_enabled(),
        threshold=Config.FACE_SIMILARITY_THRESHOLD,
    ), 200


@face_bp.post("/verify")
@jwt_required()
def verify():
    """Verify two face images against each other via CompreFace.

    Expects JSON: {"source": "<base64 jpg>", "target": "<base64 jpg>"}
    Returns the similarity and whether it clears the configured threshold.
    """
    if not Config.face_enabled():
        return (
            jsonify(
                enabled=False,
                msg="Face verification is not configured. Set COMPREFACE_URL "
                "and COMPREFACE_API_KEY to enable it.",
            ),
            503,
        )

    data = request.get_json(silent=True) or {}
    try:
        source = base64.b64decode(data["source"], validate=True)
        target = base64.b64decode(data["target"], validate=True)
    except (KeyError, binascii.Error):
        return jsonify(msg="source and target base64 images are required"), 400

    try:
        response = requests.post(
            f"{Config.COMPREFACE_URL}/api/v1/verification/verify",
            headers={"x-api-key": Config.COMPREFACE_API_KEY},
            files={
                "source_image": ("source.jpg", source, "image/jpeg"),
                "target_image": ("target.jpg", target, "image/jpeg"),
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify(msg=f"CompreFace request failed: {exc}"), 502

    payload = response.json()
    similarity = _extract_similarity(payload)
    verified = similarity is not None and similarity >= Config.FACE_SIMILARITY_THRESHOLD
    return jsonify(verified=verified, similarity=similarity, raw=payload), 200


def _extract_similarity(payload: dict) -> float | None:
    """Pull the top similarity score out of a CompreFace verification response."""
    try:
        matches = payload["result"][0]["face_matches"]
        return max(match["similarity"] for match in matches)
    except (KeyError, IndexError, ValueError):
        return None
