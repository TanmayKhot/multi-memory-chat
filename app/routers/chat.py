from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..clients.supabase_client import get_supabase_client
from ..clients.mem0_client import search_memory_records
from ..models.schemas import ChatSend
import logging
import traceback

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.get("/memories/{memory_id}/messages")
async def list_messages(memory_id: str, user=Depends(get_current_user)):
    logger.info(f"💬 Listing messages for memory: {memory_id}, user: {user['id']}")
    try:
        sb = get_supabase_client()
        resp = sb.table("chat_messages").select("*").eq("memory_id", memory_id).eq("user_id", user["id"]).order("created_at", desc=True).execute()
        logger.info(f"   Found {len(resp.data or [])} messages")
        return resp.data or []
    except Exception as e:
        logger.error(f"❌ Error listing messages: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to list messages: {str(e)}")


@router.post("/send")
async def send_message(payload: ChatSend, user=Depends(get_current_user)):
    logger.info(f"💬 Sending message for memory: {payload.memory_id}, user: {user['id']}")
    logger.info(f"   Message: {payload.message[:100]}..." if len(payload.message) > 100 else f"   Message: {payload.message}")
    
    try:
        sb = get_supabase_client()
        
        # Optional: search for relevant records using Mem0
        logger.info(f"   Searching relevant records...")
        relevant_records = search_memory_records(
            user_id=user["id"],
            memory_id=payload.memory_id,
            query=payload.message,
            limit=3
        )
        logger.info(f"   Found {len(relevant_records)} relevant records")
        
        # Store user message; prune handled by DB trigger
        data = {
            "memory_id": payload.memory_id,
            "user_id": user["id"],
            "role": "user",
            "content": payload.message,
        }
        user_msg = sb.table("chat_messages").insert(data).select("*").single().execute().data
        logger.info(f"✅ Message stored: {user_msg['id']}")
        
        # In v1, we only store user messages. 
        # Future: generate assistant reply using relevant_records as context.
        return {
            "message": user_msg,
            "relevant_context": relevant_records  # Optional: can be used by frontend or future LLM
        }
    except Exception as e:
        logger.error(f"❌ Error sending message: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
