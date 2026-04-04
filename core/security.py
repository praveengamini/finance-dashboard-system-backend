import httpx
import jwt
from functools import lru_cache
from fastapi import HTTPException, Header
from sqlalchemy import select

from core.config import settings
from db.database import SessionLocal
from db.models import Profile


@lru_cache(maxsize=1)
def get_jwks() -> dict:
    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_signing_key(token: str):
    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Malformed token")

    jwks = get_jwks()
    keys = jwks.get("keys", [])
    kid = header.get("kid")

    matched_key = None
    for key in keys:
        if kid and key.get("kid") != kid:
            continue
        matched_key = key
        break

    if not matched_key:
        get_jwks.cache_clear()
        for key in get_jwks().get("keys", []):
            if kid and key.get("kid") != kid:
                continue
            matched_key = key
            break

    if not matched_key:
        raise HTTPException(status_code=401, detail="Token signing key not found")

    kty = matched_key.get("kty")

    if kty == "RSA":
        return jwt.algorithms.RSAAlgorithm.from_jwk(matched_key), "RS256"

    if kty == "EC":
        return jwt.algorithms.ECAlgorithm.from_jwk(matched_key), "ES256"

    if kty == "oct":
        import base64
        raw = base64.urlsafe_b64decode(matched_key["k"] + "==")
        return raw, "HS256"

    raise HTTPException(status_code=401, detail=f"Unsupported key type: {kty}")


async def get_current_user(authorization: str = Header(...)):
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        signing_key, algorithm = get_signing_key(token)
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[algorithm],
            options={
                "verify_aud": False,
                "verify_iat": False,
            },
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    async with SessionLocal() as session:
        result = await session.execute(
            select(Profile).where(Profile.id == user_id)
        )
        profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    if profile.status != "active":
        raise HTTPException(status_code=403, detail="Account is inactive")

    return {"id": user_id, "role": profile.role}