"""Redis-based memory management for chat sessions"""
import json
import redis # type: ignore
from typing import Dict, Any, List, Optional
from app.config import get_settings

settings = get_settings()


class MemoryManager:
    """Manages chat session state and conversation history using Redis"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password if settings.redis_password else None,
            decode_responses=True
        )
        self.ttl = settings.session_ttl
    
    def _state_key(self, session_id: str) -> str:
        """Generate Redis key for session state"""
        return f"chat:{session_id}:state"
    
    def _history_key(self, session_id: str) -> str:
        """Generate Redis key for conversation history"""
        return f"chat:{session_id}:history"
    
    def _context_key(self, session_id: str) -> str:
        """Generate Redis key for extracted context"""
        return f"chat:{session_id}:context"
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session state
        
        Returns:
            {
                "current_function": "create_menu_item",
                "collected_arguments": {"name": "roti"},
                "missing_fields": ["price", "group_id"],
                "status": "collecting"
            }
        """
        state_json = self.redis_client.get(self._state_key(session_id))
        if not state_json:
            return {
                "current_function": None,
                "collected_arguments": {},
                "missing_fields": [],
                "status": "idle"
            }
        return json.loads(state_json)
    
    def set_session_state(
        self,
        session_id: str,
        current_function: Optional[str],
        collected_arguments: Dict[str, Any],
        missing_fields: List[str],
        status: str = "collecting"
    ):
        """Save session state to Redis"""
        state = {
            "current_function": current_function,
            "collected_arguments": collected_arguments,
            "missing_fields": missing_fields,
            "status": status
        }
        self.redis_client.setex(
            self._state_key(session_id),
            self.ttl,
            json.dumps(state)
        )
    
    def clear_session_state(self, session_id: str):
        """Clear session state after task completion"""
        self.redis_client.delete(self._state_key(session_id))
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get full conversation history
        
        Returns:
            [
                {"role": "user", "content": "create a roti"},
                {"role": "assistant", "content": "Which group?"},
                {"role": "user", "content": "breads"}
            ]
        """
        history_json = self.redis_client.get(self._history_key(session_id))
        if not history_json:
            return []
        return json.loads(history_json)
    
    def add_to_history(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Add a message to conversation history"""
        history = self.get_conversation_history(session_id)
        history.append({"role": role, "content": content})
        
        # Keep last 20 messages to avoid token limits
        if len(history) > 20:
            history = history[-20:]
        
        self.redis_client.setex(
            self._history_key(session_id),
            self.ttl,
            json.dumps(history)
        )
    
    def clear_history(self, session_id: str):
        """Clear conversation history"""
        self.redis_client.delete(self._history_key(session_id))
    
    def set_context(
        self,
        session_id: str,
        context_data: Dict[str, Any]
    ):
        """
        Store extracted context (e.g., available groups, restaurant info)
        
        Args:
            context_data: {"groups": [...], "restaurant_info": {...}}
        """
        self.redis_client.setex(
            self._context_key(session_id),
            self.ttl,
            json.dumps(context_data)
        )
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get stored context data"""
        context_json = self.redis_client.get(self._context_key(session_id))
        if not context_json:
            return {}
        return json.loads(context_json)
    
    def clear_context(self, session_id: str):
        """Clear cached context data"""
        self.redis_client.delete(self._context_key(session_id))
    
    def clear_all(self, session_id: str):
        """Clear all data for a session"""
        self.redis_client.delete(
            self._state_key(session_id),
            self._history_key(session_id),
            self._context_key(session_id)
        )
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except:
            return False


# Global memory manager instance
memory_manager = MemoryManager()