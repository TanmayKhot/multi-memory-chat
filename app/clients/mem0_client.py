from mem0 import Memory
from ..config import load_settings


def get_mem0_client():
    """
    Initialize Mem0 client with config.
    For now, we use the default in-memory store.
    In production, configure with Supabase vector store or Qdrant.
    """
    settings = load_settings()
    config = {}
    
    # If OpenAI key is set, use it for embeddings
    if settings.openai_api_key:
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": "gpt-4o-mini",
                "api_key": settings.openai_api_key,
            }
        }
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small",
                "api_key": settings.openai_api_key,
            }
        }
    
    return Memory.from_config(config)


def add_memory_record(user_id: str, memory_id: str, record_id: str, content: str):
    """Register a record with Mem0 for semantic search."""
    try:
        mem0 = get_mem0_client()
        mem0.add(
            content,
            user_id=user_id,
            metadata={
                "memory_id": memory_id,
                "record_id": record_id,
            }
        )
    except Exception as e:
        print(f"Mem0 add failed: {e}")


def search_memory_records(user_id: str, memory_id: str, query: str, limit: int = 5):
    """Search relevant records for a given query within a memory context."""
    try:
        mem0 = get_mem0_client()
        results = mem0.search(
            query,
            user_id=user_id,
            limit=limit,
        )
        # Filter by memory_id
        filtered = [
            r for r in results
            if r.get("metadata", {}).get("memory_id") == memory_id
        ]
        return filtered[:limit]
    except Exception as e:
        print(f"Mem0 search failed: {e}")
        return []

