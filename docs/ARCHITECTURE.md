# Architecture

This document expands on the design summarised in the README and maps it back to
the original capstone report.

## The core idea

In a public cloud, the provider controls the servers, so users must *trust* the
provider not to read their data. This project inserts an **independent
authenticator** between the user and the cloud. Because the authenticator — not
the cloud host — issues and verifies the token that gates every request, a
transaction originating *inside* the cloud environment (e.g. an over-curious
host) is unstamped and therefore invalid.

## Components

### 1. Authenticator (Flask backend)

- **`config.py`** — all runtime configuration is read from environment variables
  (`.env` supported), so nothing sensitive is hard-coded.
- **`database.py`** — a minimal SQLite layer built on the standard library. It
  stores users (with salted password hashes) and their files. A context-managed
  `connect()` helper guarantees connections are committed *and closed* (important
  on Windows, where a leaked connection locks the DB file).
- **`auth.py`** — registration, login (token issuance), logout (token
  revocation) and profile lookup.
- **`protected.py`** — the token-gated cloud resources. Ownership is enforced
  here: reading another user's file returns `403`.
- **`face.py`** — an optional proxy to CompreFace for biometric verification.
- **`__init__.py`** — the application factory wires up CORS, the JWT manager, and
  the JWT lifecycle callbacks that produce the report's exact status codes.

### 2. Web app (React frontend)

- **`api.js`** — a small `fetch` wrapper. It reads/writes the token in
  `sessionStorage` and attaches `Authorization: Bearer <token>` to authenticated
  calls — the mechanism at the heart of the report.
- **`auth/AuthContext.jsx`** — React context that holds the session, syncs the
  token from session storage on load, and exposes `login` / `logout`.
- **`pages/`** — Home, Login, Dashboard (the "user account interface"), and the
  post-logout "Thank you" screen from the report's snapshots.
- **`components/ProtectedRoute.jsx`** — redirects unauthenticated users to login.

## Token lifecycle & status codes

| Situation                              | HTTP status | Where enforced            |
| -------------------------------------- | ----------- | ------------------------- |
| No `Authorization` header              | `401`       | `unauthorized_loader`     |
| Expired token                          | `401`       | `expired_token_loader`    |
| Token revoked (after logout)           | `401`       | `revoked_token_loader`    |
| Malformed token                        | `422`       | `invalid_token_loader`    |
| Valid token, resource not owned        | `403`       | `protected.read_file`     |
| Valid token, authorized                | `200`       | route handler             |

These mirror Chapter 7 (Implementation) and Chapter 9 (Testing) of the report.

## Why SQLite + in-memory revocation?

The goal is a faithful, self-contained reference that anyone can clone and run in
under two minutes. SQLite needs no server, and an in-process revocation set is
enough to demonstrate genuine server-side logout. The [roadmap](../README.md#-roadmap--future-enhancements)
notes what to swap in for a production deployment (Redis, object storage, refresh
tokens).

## Mapping to the report

| Report section                     | Implementation                                  |
| ---------------------------------- | ----------------------------------------------- |
| Ch. 6 System Architecture          | `flowchart` in README + `__init__.py` wiring    |
| Ch. 6 Data Flow Diagram            | `sequenceDiagram` in README                     |
| Ch. 7 Creating a token (JWT)       | `auth.create_token` (Flask-JWT-Extended)        |
| Ch. 7 Storing the token            | `frontend/src/api.js` (`sessionStorage`)         |
| Ch. 7 Requesting with the token    | `frontend/src/api.js` (`Authorization` header)  |
| Ch. 7 Face API inclusion           | `face.py` (CompreFace proxy)                     |
| Ch. 8 Results (snapshots)          | `pages/Home`, `Login`, `Dashboard`, `Logout`    |
| Ch. 9 Testing (401/403/200)        | `tests/test_auth.py` + JWT loaders              |
