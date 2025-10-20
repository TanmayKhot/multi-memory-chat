from fastapi import Depends, HTTPException, Header
from typing import Optional
from supabase import create_client
from .config import load_settings
import logging

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    logger.info("🔐 Authenticating user...")
    
    if not authorization or not authorization.lower().startswith("bearer "):
        logger.warning("❌ Missing bearer token")
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    token_preview = token[:10] + "..." if len(token) > 10 else token
    logger.info(f"   Token: {token_preview}")
    
    settings = load_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        logger.error("❌ Supabase not configured")
        raise HTTPException(status_code=500, detail="Supabase not configured")

    supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
    try:
        user = supabase.auth.get_user(token)
    except Exception as exc:
        logger.error(f"❌ Invalid token: {str(exc)}")
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    if not user or not getattr(user, "user", None):
        logger.error("❌ Invalid token: no user found")
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info(f"✅ User authenticated: {user.user.id}")
    # Return a simple dict with user id
    return {"id": user.user.id}
