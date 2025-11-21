"""FastAPI application entry point"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.config import get_settings
from app.db import get_db, init_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_session_service import chat_service

# Import actions to register functions
from app.actions import dashboard, menu

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup: Initialize database
    init_db()
    print("Database initialized")
    print(f"Registered functions: {len(chat_service.function_registry.get_function_specs())}")
    yield
    # Shutdown: cleanup if needed
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Restaurant Management Chatbot",
    description="LLM-powered chatbot for restaurant management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Restaurant Management Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "registered_functions": len(chat_service.function_registry.get_function_specs())
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Main chat endpoint for processing user messages
    
    Args:
        request: Chat request with session_id, owner_id, restaurant_id, and message
        db: Database session
        
    Returns:
        Chat response with reply and type
    """
    try:
        response = await chat_service.process_message(db=db, request=request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/functions")
async def list_functions():
    """List all available functions"""
    functions = chat_service.function_registry.get_function_specs()
    return {
        "count": len(functions),
        "functions": functions
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
