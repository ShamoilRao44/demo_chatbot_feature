"""FastAPI application entry point"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.config import get_settings
from app.db import get_db, init_db
from app.schemas import ChatRequest, ChatResponse
from app.agent.router import process_chat
from app.agent.memory import memory_manager
from app.agent.function_registry import function_registry
from app.agent.tools import dashboard_tools, menu_tools, groups_tools, reports_tools, extras_tools, orders_tools

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Database initialized")
    print(f"Registered functions: {len(function_registry.get_function_specs())}")
    yield
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
    redis_ok = memory_manager.ping()
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
        "registered_functions": len(function_registry.get_function_specs())
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        response = await process_chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/functions")
async def list_functions():
    functions = function_registry.get_function_specs()
    return {"count": len(functions), "functions": functions}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )