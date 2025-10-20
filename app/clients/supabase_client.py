from supabase import create_client, Client
from ..config import load_settings
import logging

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    settings = load_settings()
    logger.debug(f"Creating Supabase client for URL: {settings.supabase_url[:30]}...")
    return create_client(settings.supabase_url, settings.supabase_anon_key)
