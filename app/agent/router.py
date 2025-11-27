"""Main chat router - orchestrates LLM, memory, and function execution"""
import uuid
from typing import Dict, Any
from app.schemas import ChatRequest, ChatResponse, LLMRequest
from app.agent.memory import memory_manager
from app.agent.llm_client import llm_client
from app.agent.function_registry import function_registry
from app.utils import backend_client


# Functions that require group context
FUNCTIONS_NEEDING_GROUPS = [
    "create_menu_item",
    "get_menu_items"
]


async def fetch_restaurant_context(
    restaurant_id: int, 
    session_id: str,
    function_name: str = None
) -> Dict[str, Any]:
    """
    Fetch restaurant context ONLY when needed
    
    Args:
        restaurant_id: Restaurant ID
        session_id: Session ID for caching
        function_name: Current function being executed
        
    Returns:
        Context dict (may be empty if groups not needed)
    """
    # Check if already cached
    cached = memory_manager.get_context(session_id)
    if cached:
        return cached
    
    context = {"restaurant_id": restaurant_id}
    
    # Only fetch groups if function needs them
    if function_name in FUNCTIONS_NEEDING_GROUPS:
        print(f"🔍 Fetching groups for function: {function_name}")
        groups_response = await backend_client.post("/groups/", {"r_id": restaurant_id})
        
        if groups_response.get("status") == "200":
            groups_data = groups_response.get("data", {}).get("groups", [])
            context["groups"] = [
                {
                    "id": g.get("g_id"),
                    "name": g.get("gname"),
                    "icon": g.get("g_icon")
                }
                for g in groups_data
            ]
        else:
            context["groups"] = []
    else:
        print(f"⏭️  Skipping group fetch for function: {function_name}")
        context["groups"] = []
    
    # Cache for this session
    memory_manager.set_context(session_id, context)
    
    return context


async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat processing pipeline
    
    Flow:
    1. Set access token (if provided)
    2. Generate/validate session_id
    3. Load session state from Redis
    4. Load conversation history from Redis
    5. Conditionally fetch restaurant context
    6. Call LLM with full context
    7. Handle response (ask_user or call_function)
    8. Update Redis
    9. Clear access token
    10. Return response
    """
    
    try:
        # Step 1: Set access token ONLY if provided
        if request.access_token:
            backend_client.set_access_token(request.access_token)
            print(f"🔐 Access token set")
        else:
            print(f"🔓 No access token (public endpoint)")
        
        # Step 2: Generate session_id if not provided
        if not request.session_id:
            session_id = f"session-{uuid.uuid4()}"
            print(f"🆕 Auto-generated session: {session_id}")
        else:
            session_id = request.session_id
        
        # Handle special commands
        if request.message.lower().strip() in ["cancel", "reset", "clear", "start over"]:
            memory_manager.clear_all(session_id)
            return ChatResponse(
                type="reset",
                reply="Conversation cleared. What would you like to do?",
                session_id=session_id
            )
        
        # Step 3: Load session state
        session_state = memory_manager.get_session_state(session_id)
        current_function = session_state.get('current_function')
        print(f"📊 Session state: {session_state['status']}, Function: {current_function}")
        
        # Step 4: Load conversation history
        conversation_history = memory_manager.get_conversation_history(session_id)
        print(f"💬 History: {len(conversation_history)} messages")
        
        # Step 5: Fetch context ONLY if current function needs groups
        restaurant_context = await fetch_restaurant_context(
            request.restaurant_id, 
            session_id,
            current_function
        )
        print(f"🏪 Context: {len(restaurant_context.get('groups', []))} groups")
        
        # Step 6: Build LLM request
        llm_request = LLMRequest(
            message=request.message,
            session_state=session_state,
            conversation_history=conversation_history,
            restaurant_context=restaurant_context,
            available_functions=function_registry.get_function_specs()
        )
        
        # Step 7: Get LLM response
        try:
            llm_response = await llm_client.get_completion(llm_request)
            print(f"🤖 LLM says: {llm_response.type}")
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return ChatResponse(
                type="error",
                reply=f"I encountered an error: {str(e)}",
                session_id=session_id
            )
        
        # Add user message to history
        memory_manager.add_to_history(session_id, "user", request.message)
        
        # Step 8: Handle LLM response
        if llm_response.type == "ask_user":
            # Save state for multi-turn collection
            memory_manager.set_session_state(
                session_id=session_id,
                current_function=llm_response.current_function,
                collected_arguments=llm_response.partial_arguments or {},
                missing_fields=llm_response.missing_fields or [],
                status="collecting"
            )
            
            # Add bot message to history
            memory_manager.add_to_history(session_id, "assistant", llm_response.message)
            
            # Check for context switch
            if current_function and llm_response.current_function != current_function:
                print(f"🔄 Context switch: {current_function} → {llm_response.current_function}")
                # Clear old context when switching functions
                memory_manager.clear_context(session_id)
            
            return ChatResponse(
                type="ask_user",
                reply=llm_response.message,
                session_id=session_id,
                missing_fields=llm_response.missing_fields
            )
        
        elif llm_response.type == "call_function":
            # Execute function
            function_name = llm_response.name
            arguments = llm_response.arguments or {}
            
            # Ensure restaurant_id is in arguments
            if "restaurant_id" not in arguments:
                arguments["restaurant_id"] = request.restaurant_id
            
            print(f"⚡ Executing: {function_name} with args: {arguments}")
            
            try:
                # Execute function (no db_session parameter)
                result = await function_registry.execute_function(function_name, arguments)
                print(f"✅ Result: {result[:100]}...")
                
                # Clear session state after successful execution
                memory_manager.clear_session_state(session_id)
                
                # Add result to history
                memory_manager.add_to_history(session_id, "assistant", result)
                
                # Clear context cache to force refresh on next request
                memory_manager.clear_context(session_id)
                
                return ChatResponse(
                    type="result",
                    reply=result,
                    session_id=session_id,
                    function=function_name
                )
            
            except Exception as e:
                print(f"❌ Function error: {e}")
                import traceback
                traceback.print_exc()
                error_msg = f"Error executing {function_name}: {str(e)}"
                memory_manager.add_to_history(session_id, "assistant", error_msg)
                
                return ChatResponse(
                    type="error",
                    reply=error_msg,
                    session_id=session_id
                )
        
        else:
            # Unknown response type
            return ChatResponse(
                type="error",
                reply="I didn't understand that. Could you please rephrase?",
                session_id=session_id
            )
    
    finally:
        # Step 9: ALWAYS clear access token after request completes
        backend_client.clear_access_token()
        print(f"🔓 Access token cleared")