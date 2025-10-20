from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..clients.supabase_client import get_supabase_client
from ..models.schemas import MemoryCreate, MemoryUpdate
import logging
import traceback

router = APIRouter(prefix="/memories", tags=["memories"])
logger = logging.getLogger(__name__)


@router.get("")
async def list_memories(user=Depends(get_current_user)):
    logger.info(f"📋 Listing memories for user: {user['id']}")
    try:
        sb = get_supabase_client()
        resp = sb.table("memories").select("*").eq("user_id", user["id"]).order("created_at", desc=True).execute()
        logger.info(f"   Found {len(resp.data or [])} memories")
        return resp.data or []
    except Exception as e:
        logger.error(f"❌ Error listing memories: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to list memories: {str(e)}")


@router.post("")
async def create_memory(payload: MemoryCreate, user=Depends(get_current_user)):
    logger.info(f"✨ Creating memory for user: {user['id']}")
    logger.info(f"   Title: {payload.title}")
    logger.info(f"   Description: {payload.description}")
    
    try:
        sb = get_supabase_client()
        data = {
            "user_id": user["id"],
            "title": payload.title,
            "description": payload.description,
        }
        logger.info(f"   Data to insert: {data}")
        
        resp = sb.table("memories").insert(data).select("*").single().execute()
        logger.info(f"✅ Memory created successfully: {resp.data}")
        return resp.data
    except Exception as e:
        logger.error(f"❌ Error creating memory: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {str(e)}")


@router.patch("/{memory_id}")
async def update_memory(memory_id: str, payload: MemoryUpdate, user=Depends(get_current_user)):
    sb = get_supabase_client()
    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not changes:
        return {"updated": False}
    resp = sb.table("memories").update(changes).eq("id", memory_id).eq("user_id", user["id"]).select("*").single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Not found")
    return resp.data


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user=Depends(get_current_user)):
    sb = get_supabase_client()
    resp = sb.table("memories").delete().eq("id", memory_id).eq("user_id", user["id"]).execute()
    return {"deleted": True, "count": resp.count}
