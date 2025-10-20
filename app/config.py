import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_db_url: str
    openai_api_key: str | None = None


def load_settings() -> Settings:
    return Settings(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        supabase_db_url=os.getenv("SUPABASE_DB_URL", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
