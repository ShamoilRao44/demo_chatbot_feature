"""Chat session service for managing conversation state and orchestration"""
import uuid
from sqlalchemy.orm import Session
from app.models import ChatSession
from app.schemas import ChatRequest, ChatResponse, LLMRequest
from app.llm_client import llm_client
from app.function_registry import function_registry
from typing import Dict, Any


class ChatSessionService:
    """Service for managing chat sessions and orchestrating LLM interactions"""
    
    def __init__(self):
        self.llm_client = llm_client
        self.function_registry = function_registry
    
    def get_or_create_session(
        self,
        db: Session,
        session_id: str,
        owner_id: int
    ) -> ChatSession:
        """
        Get existing chat session or create new one
        
        Args:
            db: Database session
            session_id: Session identifier
            owner_id: Owner ID
            
        Returns:
            ChatSession object
        """
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if not session:
            session = ChatSession(
                id=session_id,
                owner_id=owner_id,
                status="idle",
                current_function=None,
                collected_arguments={},
                missing_fields=[],
                last_bot_message=None
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        return session
    
    def build_session_state(
        self,
        session: ChatSession,
        restaurant_id: int
    ) -> Dict[str, Any]:
        """
        Build session state for LLM context
        
        Args:
            session: Chat session
            restaurant_id: Restaurant ID
            
        Returns:
            Session state dictionary
        """
        return {
            "current_function": session.current_function,
            "collected_arguments": session.collected_arguments or {},
            "missing_fields": session.missing_fields or [],
            "status": session.status,
            "restaurant_id": restaurant_id
        }
    
    def update_session_from_llm_response(
        self,
        db: Session,
        session: ChatSession,
        llm_response: Any
    ):
        """
        Update chat session based on LLM response with smart context switching
        
        Args:
            db: Database session
            session: Chat session
            llm_response: LLM response object
        """
        if llm_response.type == "ask_user":
            # Check if function changed (context switch detected)
            if session.current_function and llm_response.current_function:
                if session.current_function != llm_response.current_function:
                    print(f"🔄 Context switch detected: {session.current_function} → {llm_response.current_function}")
            
            # Update session with new/continued collection state
            session.status = "collecting"
            session.current_function = llm_response.current_function
            session.collected_arguments = llm_response.partial_arguments or {}
            session.missing_fields = llm_response.missing_fields or []
            session.last_bot_message = llm_response.message
        
        elif llm_response.type == "call_function":
            # Clear session state after function execution
            session.status = "idle"
            session.current_function = None
            session.collected_arguments = {}
            session.missing_fields = []
            session.last_bot_message = None
        
        db.commit()
    
    def handle_special_commands(
        self,
        db: Session,
        session: ChatSession,
        message: str
    ) -> ChatResponse:
        """
        Handle special commands like cancel, reset, etc.
        
        Args:
            db: Database session
            session: Chat session
            message: User message
            
        Returns:
            ChatResponse if special command handled, None otherwise
        """
        message_lower = message.lower().strip()
        cancel_keywords = ["cancel", "reset", "start over", "nevermind", "forget it", "clear"]
        
        if message_lower in cancel_keywords:
            # Clear session state
            session.current_function = None
            session.collected_arguments = {}
            session.missing_fields = []
            session.status = "idle"
            session.last_bot_message = None
            db.commit()
            
            return ChatResponse(
                reply="Okay, I've cleared our conversation. What would you like to do?",
                type="reset",
                session_id=session.id
            )
        
        return None
    
    async def process_message(
        self,
        db: Session,
        request: ChatRequest
    ) -> ChatResponse:
        """
        Process user message and orchestrate response
        
        Args:
            db: Database session
            request: Chat request
            
        Returns:
            Chat response
        """
        # Auto-generate session_id if not provided
        if not request.session_id:
            session_id = f"session-{uuid.uuid4()}"
            print(f"🆕 Auto-generated session_id: {session_id}")
        else:
            session_id = request.session_id
        
        # Get or create session
        session = self.get_or_create_session(
            db=db,
            session_id=session_id,
            owner_id=request.owner_id
        )
        
        # Check for special commands (cancel, reset, etc.)
        special_response = self.handle_special_commands(db, session, request.message)
        if special_response:
            return special_response
        
        # Build session state
        session_state = self.build_session_state(
            session=session,
            restaurant_id=request.restaurant_id
        )
        
        # Get available functions
        available_functions = self.function_registry.get_function_specs()
        
        # Build LLM request
        llm_request = LLMRequest(
            message=request.message,
            session_state=session_state,
            available_functions=available_functions,
            restaurant_id=request.restaurant_id
        )
        
        # Get LLM response
        try:
            llm_response = await self.llm_client.get_completion(llm_request)
        except Exception as e:
            return ChatResponse(
                reply=f"I encountered an error: {str(e)}",
                type="error",
                session_id=session_id
            )
        
        # Handle LLM response
        if llm_response.type == "ask_user":
            # LLM needs more information
            self.update_session_from_llm_response(db, session, llm_response)
            
            return ChatResponse(
                reply=llm_response.message,
                type="ask_user",
                session_id=session_id
            )
        
        elif llm_response.type == "call_function":
            # LLM has all information, execute function
            function_name = llm_response.name
            arguments = llm_response.arguments or {}
            
            # Add restaurant_id to arguments if not present
            if "restaurant_id" not in arguments:
                arguments["restaurant_id"] = request.restaurant_id
            
            try:
                # Execute function
                result = await self.function_registry.execute_function(
                    name=function_name,
                    arguments=arguments,
                    db_session=db
                )
                
                # Clear session state
                self.update_session_from_llm_response(db, session, llm_response)
                
                return ChatResponse(
                    reply=result,
                    type="result",
                    function=function_name,
                    session_id=session_id
                )
            
            except KeyError as e:
                return ChatResponse(
                    reply=f"Unknown function: {function_name}",
                    type="error",
                    session_id=session_id
                )
            except Exception as e:
                return ChatResponse(
                    reply=f"Error executing function: {str(e)}",
                    type="error",
                    session_id=session_id
                )
        
        else:
            # Unknown response type
            return ChatResponse(
                reply="I didn't understand that. Could you please rephrase?",
                type="ask_user",
                session_id=session_id
            )


# Global service instance
chat_service = ChatSessionService()