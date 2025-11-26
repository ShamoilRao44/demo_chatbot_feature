"""Pydantic schemas for Chhotu Brain chatbot"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


# ============================================================================
# CHAT REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request from user/frontend"""
    session_id: Optional[str] = Field(None, description="Session ID (auto-generated if not provided)")
    restaurant_id: int = Field(..., description="Restaurant ID")
    owner_id: int = Field(..., description="Owner ID")
    message: str = Field(..., description="User message in any language")


class ChatResponse(BaseModel):
    """Chat response to user/frontend"""
    type: str = Field(..., description="Response type: ask_user, result, or error")
    reply: str = Field(..., description="Message to display to user")
    session_id: str = Field(..., description="Session ID for tracking")
    function: Optional[str] = Field(None, description="Function executed (if type=result)")
    missing_fields: Optional[List[str]] = Field(None, description="Fields still needed (if type=ask_user)")


# ============================================================================
# INTERNAL LLM MODELS (used internally by agent)
# ============================================================================

class LLMRequest(BaseModel):
    """Internal request to LLM"""
    message: str
    session_state: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    restaurant_context: Dict[str, Any]
    available_functions: List[Dict[str, Any]]


class LLMResponse(BaseModel):
    """LLM response (parsed from JSON)"""
    type: str  # ask_user or call_function
    message: Optional[str] = None
    missing_fields: Optional[List[str]] = None
    current_function: Optional[str] = None
    partial_arguments: Optional[Dict[str, Any]] = None
    name: Optional[str] = None  # function name
    arguments: Optional[Dict[str, Any]] = None


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    redis: str
    ollama: str
    registered_functions: int