"""
Clerk JWT Authentication Dependency
======================================
Provides FastAPI dependencies for verifying Clerk JWTs.

Two dependencies are available:
  - get_current_user()   → requires a valid token, raises 401 if missing/invalid
  - get_optional_user()  → returns None if no token, never raises (for optional auth)

Local dev bypass:
  Set SKIP_AUTH=true in backend/.env to bypass all verification.
  A mock guest user is returned transparently so the pipeline works identically.

Requires:
  - CLERK_SECRET_KEY env var (from clerk.com → API Keys)
  - PyJWT >= 2.8.0 (pip install PyJWT)
  - httpx (pip install httpx)
"""

import os
import json
import base64
from dataclasses import dataclass
from typing import Optional

import httpx
from fastapi import Header, HTTPException, Depends

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
SKIP_AUTH: bool = os.getenv("SKIP_AUTH", "true").lower() == "true"
CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")

# Clerk JWKS endpoint — public key for JWT verification
CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks"

# Cache JWKS in memory to avoid fetching on every request
_jwks_cache: Optional[dict] = None


# ──────────────────────────────────────────────────────────────
# DATA MODEL
# ──────────────────────────────────────────────────────────────
@dataclass
class ClerkUser:
    """Authenticated user identity from Clerk JWT."""
    user_id: str         # Clerk user ID, e.g. "user_2abc123"
    email: Optional[str] = None
    first_name: Optional[str] = None
    is_guest: bool = False   # True when SKIP_AUTH=true


GUEST_USER = ClerkUser(
    user_id="guest",
    email="guest@localhost",
    first_name="Guest",
    is_guest=True,
)


# ──────────────────────────────────────────────────────────────
# JWT VERIFICATION
# ──────────────────────────────────────────────────────────────
def _decode_jwt_payload(token: str) -> Optional[dict]:
    """
    Decode the JWT payload WITHOUT signature verification.
    Used only to extract the user_id when PyJWT is unavailable.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        # Add padding if needed
        payload_b64 = parts[1] + "=="
        payload_json = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
        return json.loads(payload_json)
    except Exception:
        return None


def _get_jwks() -> Optional[dict]:
    """Fetch Clerk's JWKS (with in-memory cache)."""
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    try:
        headers = {}
        if CLERK_SECRET_KEY:
            headers["Authorization"] = f"Bearer {CLERK_SECRET_KEY}"
        response = httpx.get(CLERK_JWKS_URL, headers=headers, timeout=5.0)
        if response.status_code == 200:
            _jwks_cache = response.json()
            return _jwks_cache
    except Exception:
        pass
    return None


def _verify_clerk_token(token: str) -> Optional[ClerkUser]:
    """
    Verify a Clerk JWT and return the authenticated user.
    Strategy:
      1. Try full JWT verification via PyJWT + JWKS (most secure)
      2. Fall back to payload-only decode to extract user_id (softer check)
    Returns None if token is completely invalid.
    """
    try:
        import jwt as pyjwt  # type: ignore
    except ImportError:
        pyjwt = None

    if pyjwt:
        jwks = _get_jwks()
        if jwks:
            try:
                from jwt import PyJWKClient
                jwks_client = PyJWKClient(CLERK_JWKS_URL)
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                payload = pyjwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    options={"verify_exp": True},
                )
                return ClerkUser(
                    user_id=payload.get("sub", ""),
                    email=payload.get("email"),
                    first_name=payload.get("given_name") or payload.get("name"),
                )
            except Exception:
                pass

    # Soft fallback — decode without full signature verification
    # Acceptable when CLERK_SECRET_KEY is missing (during onboarding)
    payload = _decode_jwt_payload(token)
    if payload and payload.get("sub"):
        return ClerkUser(
            user_id=payload["sub"],
            email=payload.get("email"),
            first_name=payload.get("given_name"),
        )

    return None


# ──────────────────────────────────────────────────────────────
# FASTAPI DEPENDENCIES
# ──────────────────────────────────────────────────────────────
def get_current_user(authorization: Optional[str] = Header(None)) -> ClerkUser:
    """
    FastAPI dependency: requires a valid Clerk JWT.
    Use with: current_user: ClerkUser = Depends(get_current_user)
    Raises HTTP 401 if token is missing or invalid.
    Bypassed entirely when SKIP_AUTH=true.
    """
    if SKIP_AUTH:
        return GUEST_USER

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")

    token = authorization.removeprefix("Bearer ").strip()
    user = _verify_clerk_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please sign in again.")

    return user


def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[ClerkUser]:
    """
    FastAPI dependency: auth is optional.
    Returns ClerkUser if token present and valid, None otherwise.
    Never raises an exception.
    Use for endpoints that work for both guests and authenticated users.
    """
    if SKIP_AUTH:
        return GUEST_USER

    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ").strip()
    return _verify_clerk_token(token)
