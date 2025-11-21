"""LLM client for Ollama integration"""
import httpx
import json
from typing import Dict, Any, List
from app.config import get_settings
from app.schemas import LLMRequest, LLMResponse

settings = get_settings()


class LLMClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM"""
        return """You are a restaurant management assistant. Your job is to help restaurant owners manage their business through natural conversation.

You have access to specific functions that can modify restaurant data. When a user requests something, you must:

1. Identify which function they want to use
2. Collect ALL required parameters through conversation
3. Once you have all parameters, execute the function

CONTEXT SWITCHING AND FLEXIBILITY:
- If the user changes their mind mid-conversation, RESPECT their new intent
- Example: User starts creating an item, then says "actually create a group first"
  → Immediately start collecting info for create_menu_group instead
  → The previous incomplete task is automatically cancelled
- If the user seems to want something different, switch to the new task
- Don't force them to complete a task if they clearly want to do something else
- Be natural and conversational - follow the user's lead

HANDLING CONTEXT CHANGES:
- When user says "no", "wait", "actually", "instead", "let's do X first" → They're changing their mind
- Clear any previous partial collection and start fresh with the new intent
- Acknowledge the change naturally: "Okay, let's do that instead. What..."
- If truly ambiguous, ask: "Should I cancel [old task] and do [new task] instead?"

CRITICAL RESPONSE FORMAT:

You MUST respond with ONLY valid JSON in one of these two formats:

FORMAT 1 - When you need more information:
{
  "type": "ask_user",
  "message": "Your question to the user",
  "missing_fields": ["field1", "field2"],
  "current_function": "function_name",
  "partial_arguments": {"collected_field": "value"}
}

FORMAT 2 - When you have all information and are ready to execute:
{
  "type": "call_function",
  "name": "function_name",
  "arguments": {"param1": "value1", "param2": "value2"}
}

RULES:
- NEVER output anything except valid JSON
- NO markdown, NO explanations, NO extra text
- Be conversational in your "message" field
- Ask for ONE missing field at a time when possible
- Validate that argument types match the function spec
- If user says something unclear, ask for clarification using ask_user format
- ALWAYS adapt to the user's changing intentions"""
    
    def _build_functions_spec(self, functions: List[Dict[str, Any]]) -> str:
        """Build function specifications for the prompt"""
        specs = []
        for func in functions:
            specs.append(json.dumps(func, indent=2))
        return "\n\n".join(specs)
    
    def _build_session_context(self, session_state: Dict[str, Any]) -> str:
        """Build current session context"""
        return json.dumps(session_state, indent=2)
    
    async def get_completion(
        self,
        request: LLMRequest
    ) -> LLMResponse:
        """
        Get completion from Ollama LLM
        
        Args:
            request: LLM request with message, session state, and functions
            
        Returns:
            LLMResponse with either ask_user or call_function type
        """
        # Build the full prompt
        system_prompt = self._build_system_prompt()
        functions_spec = self._build_functions_spec(request.available_functions)
        session_context = self._build_session_context(request.session_state)
        
        # Construct messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "system",
                "content": f"AVAILABLE FUNCTIONS:\n\n{functions_spec}"
            },
            {
                "role": "system",
                "content": f"CURRENT SESSION STATE:\n{session_context}"
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
        
        # Call Ollama API
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "format": "json"  # Request JSON output
                    }
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                content = data.get("message", {}).get("content", "")
                
                # Parse JSON response
                try:
                    llm_output = json.loads(content)
                except json.JSONDecodeError:
                    # Fallback: try to extract JSON from response
                    llm_output = self._extract_json_from_text(content)
                
                # Validate and return structured response
                return self._validate_llm_response(llm_output)
                
            except httpx.HTTPError as e:
                raise Exception(f"LLM API error: {str(e)}")
            except Exception as e:
                raise Exception(f"LLM processing error: {str(e)}")
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Try to extract JSON from text that might have extra content"""
        # Try to find JSON object
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except:
                pass
        
        # Fallback to error response
        return {
            "type": "ask_user",
            "message": "I didn't quite understand that. Could you please rephrase?",
            "missing_fields": [],
            "current_function": None,
            "partial_arguments": {}
        }
    
    def _validate_llm_response(self, llm_output: Dict[str, Any]) -> LLMResponse:
        """Validate and structure LLM response"""
        response_type = llm_output.get("type")
        
        if response_type == "ask_user":
            return LLMResponse(
                type="ask_user",
                message=llm_output.get("message", ""),
                missing_fields=llm_output.get("missing_fields", []),
                current_function=llm_output.get("current_function"),
                partial_arguments=llm_output.get("partial_arguments", {})
            )
        elif response_type == "call_function":
            return LLMResponse(
                type="call_function",
                name=llm_output.get("name"),
                arguments=llm_output.get("arguments", {})
            )
        else:
            # Invalid response type, treat as ask_user
            return LLMResponse(
                type="ask_user",
                message="I need more information. What would you like to do?",
                missing_fields=[],
                current_function=None,
                partial_arguments={}
            )


# Global LLM client instance
llm_client = LLMClient()