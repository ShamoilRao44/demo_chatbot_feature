"""Ollama LLM client with conversation history support"""
import httpx
import json
from typing import Dict, Any, List
from pathlib import Path
from app.config import get_settings
from app.schemas import LLMRequest, LLMResponse

settings = get_settings()


class LLMClient:
    """Client for Ollama LLM with conversation history"""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        prompt_path = Path(__file__).parent / "prompts" / "system_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _build_function_specs(self, functions: List[Dict[str, Any]]) -> str:
        """Format function specs for prompt"""
        specs = []
        for func in functions:
            spec_str = f"Function: {func['name']}\n"
            spec_str += f"Description: {func['description']}\n"
            spec_str += f"Parameters: {json.dumps(func['parameters'], indent=2)}\n"
            specs.append(spec_str)
        return "\n---\n".join(specs)
    
    async def get_completion(self, request: LLMRequest) -> LLMResponse:
        """
        Get completion from Ollama with full context
        
        Args:
            request: LLM request with message, history, context, functions
            
        Returns:
            Parsed LLM response
        """
        # Build messages array
        messages = []
        
        # 1. System prompt
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # 2. Function specifications
        functions_text = self._build_function_specs(request.available_functions)
        messages.append({
            "role": "system",
            "content": f"AVAILABLE FUNCTIONS:\n\n{functions_text}"
        })
        
        # 3. Current session state
        session_info = f"""CURRENT SESSION STATE:
Current Function: {request.session_state.get('current_function', 'None')}
Collected Arguments: {json.dumps(request.session_state.get('collected_arguments', {}), indent=2)}
Missing Fields: {request.session_state.get('missing_fields', [])}
Status: {request.session_state.get('status', 'idle')}
"""
        messages.append({
            "role": "system",
            "content": session_info
        })
        
        # 4. Restaurant context (groups, etc.)
        if request.restaurant_context:
            context_text = f"RESTAURANT CONTEXT:\n{json.dumps(request.restaurant_context, indent=2)}"
            messages.append({
                "role": "system",
                "content": context_text
            })
        
        # 5. Conversation history
        if request.conversation_history:
            messages.extend(request.conversation_history)
        
        # 6. Current message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call Ollama
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                print(f"🤖 Calling Ollama with {len(messages)} messages...")
                
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                content = data.get("message", {}).get("content", "")
                
                print(f"✅ Ollama response received")
                
                # Parse JSON response
                try:
                    # Clean markdown if present
                    content = content.replace("```json\n", "").replace("\n```", "").strip()
                    llm_output = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
                    print(f"Raw content: {content[:500]}")
                    # Fallback response
                    llm_output = {
                        "type": "ask_user",
                        "message": "I didn't understand that clearly. Could you rephrase?",
                        "missing_fields": [],
                        "current_function": None,
                        "partial_arguments": {}
                    }
                
                return self._validate_llm_response(llm_output)
                
            except httpx.HTTPError as e:
                print(f"❌ HTTP Error: {e}")
                raise Exception(f"LLM API error: {str(e)}")
            except Exception as e:
                print(f"❌ Error: {e}")
                raise Exception(f"LLM processing error: {str(e)}")
    
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
            # Invalid response
            return LLMResponse(
                type="ask_user",
                message="I need more information. What would you like to do?",
                missing_fields=[],
                current_function=None,
                partial_arguments={}
            )


# Global LLM client instance
llm_client = LLMClient()