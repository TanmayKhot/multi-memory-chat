from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import memories, records, chat
import logging
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mem0 Multi-Memory Chat API")

# Add request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"🔵 Incoming Request: {request.method} {request.url.path}")
    logger.info(f"   Headers: {dict(request.headers)}")
    
    # Read and log body for POST/PUT/PATCH requests
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        logger.info(f"   Body: {body.decode('utf-8') if body else 'empty'}")
        # Restore body for route handler
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(f"✅ Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Error: {request.method} {request.url.path} - Time: {process_time:.3f}s")
        logger.error(f"   Exception: {str(e)}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e), "type": type(e).__name__}
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memories.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}
