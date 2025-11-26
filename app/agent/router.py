"""Main chat router - orchestrates LLM, memory, and function execution"""
import uuid
from typing import Dict, Any
from app.schemas import ChatRequest, ChatResponse, LLMRequest
from app.agent.memory import memory_manager
from app.agent.llm_client import llm_client
from app.agent.function_registry import function_registry
from app.utils import backend_client


async def fetch_restaurant_context(restaurant_id: int, session_id: str) -> Dict[str, Any]:
    """
    Fetch and cache restaurant context (groups, etc.)
    
    This reduces repeated backend calls during a conversation
    """
    # Check if already cached
    cached = memory_manager.get_context(session_id)
    if cached:
        return cached
    
    # Fetch groups from backend
    groups_response = await backend_client.post("/groups/", {"r_id": restaurant_id})
    
    context = {
        "restaurant_id": restaurant_id,
        "groups": []
    }
    
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
    
    # Cache for this session
    memory_manager.set_context(session_id, context)
    
    return context


async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat processing pipeline
    
    Flow:
    1. Generate/validate session_id
    2. Load session state from Redis
    3. Load conversation history from Redis
    4. Fetch restaurant context (cached)
    5. Call LLM with full context
    6. Handle response (ask_user or call_function)
    7. Update Redis
    8. Return response
    """
    
    # Step 1: Generate session_id if not provided
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
    
    # Step 2: Load session state
    session_state = memory_manager.get_session_state(session_id)
    print(f"📊 Session state: {session_state['status']}, Function: {session_state['current_function']}")
    
    # Step 3: Load conversation history
    conversation_history = memory_manager.get_conversation_history(session_id)
    print(f"💬 History: {len(conversation_history)} messages")
    
    # Step 4: Fetch restaurant context
    restaurant_context = await fetch_restaurant_context(request.restaurant_id, session_id)
    print(f"🏪 Context: {len(restaurant_context.get('groups', []))} groups")
    
    # Step 5: Build LLM request
    llm_request = LLMRequest(
        message=request.message,
        session_state=session_state,
        conversation_history=conversation_history,
        restaurant_context=restaurant_context,
        available_functions=function_registry.get_function_specs()
    )
    
    # Step 6: Get LLM response
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
    
    # Step 7: Handle LLM response
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
        if session_state.get("current_function") and \
           llm_response.current_function != session_state.get("current_function"):
            print(f"🔄 Context switch: {session_state.get('current_function')} → {llm_response.current_function}")
        
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
        
        print(f"⚡ Executing: {function_name}")
        
        try:
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