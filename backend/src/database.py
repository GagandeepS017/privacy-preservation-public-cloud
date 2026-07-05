"""Tiny SQLite data layer.

We use the standard-library ``sqlite3`` module instead of a heavier ORM so the
project has zero database dependencies and runs anywhere Python runs.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator, Optional

from werkzeug.security import generate_password_hash

from .config import Config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    display_name  TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id    INTEGER NOT NULL,
    name        TEXT    NOT NULL,
    content     TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users (id)
);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Yield a connection that always commits on success and always closes.

    ``with sqlite3.connect(...)`` only commits — it does not close — which on
    Windows leaves the database file locked. This wrapper guarantees closure.
    """
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables (idempotent) and seed the demo account if enabled."""
    with connect() as conn:
        conn.executescript(_SCHEMA)

    if Config.SEED_DEMO_USER:
        _seed_demo_user()


def _seed_demo_user() -> None:
    if get_user_by_email(Config.DEMO_EMAIL):
        return
    user_id = create_user(
        email=Config.DEMO_EMAIL,
        password=Config.DEMO_PASSWORD,
        display_name="Demo User",
    )
    # Give the demo user a couple of sample "cloud" files to browse.
    add_file(user_id, "welcome.txt", "Your private cloud files live here.")
    add_file(user_id, "notes.md", "# Notes\nOnly you can read this — not even the host.")


# --- Users ---------------------------------------------------------------
def create_user(email: str, password: str, display_name: Optional[str] = None) -> int:
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
            (email, generate_password_hash(password), display_name or email),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


# --- Files ---------------------------------------------------------------
def add_file(owner_id: int, name: str, content: str = "") -> int:
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO files (owner_id, name, content) VALUES (?, ?, ?)",
            (owner_id, name, content),
        )
        return int(cursor.lastrowid)


def list_files(owner_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, name, created_at FROM files WHERE owner_id = ? ORDER BY id",
            (owner_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_file(file_id: int) -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM files WHERE id = ?", (file_id,)
        ).fetchone()
        return dict(row) if row else None
