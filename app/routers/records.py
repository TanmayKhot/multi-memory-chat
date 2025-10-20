from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..clients.supabase_client import get_supabase_client
from ..clients.mem0_client import add_memory_record
from ..models.schemas import RecordCreate
import logging
import traceback

router = APIRouter(prefix="/memories/{memory_id}/records", tags=["records"])
logger = logging.getLogger(__name__)


@router.get("")
async def list_records(memory_id: str, user=Depends(get_current_user)):
    logger.info(f"📝 Listing records for memory: {memory_id}, user: {user['id']}")
    try:
        sb = get_supabase_client()
        resp = sb.table("memory_records").select("*").eq("memory_id", memory_id).eq("user_id", user["id"]).order("created_at", desc=True).execute()
        logger.info(f"   Found {len(resp.data or [])} records")
        return resp.data or []
    except Exception as e:
        logger.error(f"❌ Error listing records: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to list records: {str(e)}")


@router.post("")
async def create_record(memory_id: str, payload: RecordCreate, user=Depends(get_current_user)):
    logger.info(f"✨ Creating record for memory: {memory_id}, user: {user['id']}")
    logger.info(f"   Content: {payload.content[:100]}..." if len(payload.content) > 100 else f"   Content: {payload.content}")
    
    try:
        sb = get_supabase_client()
        data = {
            "memory_id": memory_id,
            "user_id": user["id"],
            "content": payload.content,
            "metadata": payload.metadata or {},
        }
        resp = sb.table("memory_records").insert(data).select("*").single().execute()
        record = resp.data
        logger.info(f"✅ Record created: {record['id']}")
        
        # Register with Mem0 for semantic search
        logger.info(f"   Registering with Mem0...")
        add_memory_record(
            user_id=user["id"],
            memory_id=memory_id,
            record_id=record["id"],
            content=payload.content
        )
        
        return record
    except Exception as e:
        logger.error(f"❌ Error creating record: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")


@router.delete("/{record_id}")
async def delete_record(memory_id: str, record_id: str, user=Depends(get_current_user)):
    sb = get_supabase_client()
    resp = sb.table("memory_records").delete().eq("id", record_id).eq("memory_id", memory_id).eq("user_id", user["id"]).execute()
    return {"deleted": True, "count": resp.count}
