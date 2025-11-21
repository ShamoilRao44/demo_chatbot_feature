"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatRequest(BaseModel):
    """Chat request schema"""
    session_id: Optional[str] = Field(None, description="Unique session identifier (auto-generated if not provided)")
    owner_id: int = Field(..., description="Restaurant owner ID")
    restaurant_id: int = Field(..., description="Restaurant ID")
    message: str = Field(..., description="User message")


class ChatResponse(BaseModel):
    """Chat response schema"""
    reply: str = Field(..., description="Bot reply message")
    type: str = Field(..., description="Response type: ask_user or result")
    function: Optional[str] = Field(None, description="Function name if executed")
    session_id: str = Field(..., description="Session identifier")


class LLMRequest(BaseModel):
    """Internal LLM request schema"""
    message: str
    session_state: Dict[str, Any]
    available_functions: List[Dict[str, Any]]
    restaurant_id: int


class LLMResponse(BaseModel):
    """LLM response schema"""
    type: str  # ask_user or call_function
    message: Optional[str] = None
    missing_fields: Optional[List[str]] = None
    current_function: Optional[str] = None
    partial_arguments: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None