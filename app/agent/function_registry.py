"""Function registry for managing available chatbot functions"""
from typing import Dict, Any, Callable, List, Awaitable
from dataclasses import dataclass


@dataclass
class FunctionSpec:
    """Function specification with metadata"""
    name: str
    description: str
    parameters: Dict[str, Any]


class FunctionRegistry:
    """Registry for chatbot functions and their handlers"""
    
    def __init__(self):
        self._functions: Dict[str, FunctionSpec] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register_function(self, name: str, spec: Dict[str, Any]):
        """
        Register a function specification
        
        Args:
            name: Function name
            spec: Function specification with description and parameters
        """
        self._functions[name] = FunctionSpec(
            name=name,
            description=spec.get("description", ""),
            parameters=spec.get("parameters", {})
        )
    
    def register_handler(self, name: str, handler: Callable):
        """
        Register a function handler
        
        Args:
            name: Function name
            handler: Async function that executes the action
        """
        self._handlers[name] = handler
    
    def get_function_specs(self) -> List[Dict[str, Any]]:
        """
        Get all function specifications for LLM
        
        Returns:
            List of function specs in JSON format
        """
        specs = []
        for func in self._functions.values():
            specs.append({
                "name": func.name,
                "description": func.description,
                "parameters": func.parameters
            })
        return specs
    
    def get_handler(self, name: str) -> Callable:
        """
        Get handler for a function
        
        Args:
            name: Function name
            
        Returns:
            Handler function
            
        Raises:
            KeyError: If function not found
        """
        if name not in self._handlers:
            raise KeyError(f"No handler registered for function: {name}")
        return self._handlers[name]
    
    def has_function(self, name: str) -> bool:
        """Check if function is registered"""
        return name in self._functions
    
    async def execute_function(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """
        Execute a registered function
        
        Args:
            name: Function name
            arguments: Function arguments
            
        Returns:
            Result message
        """
        handler = self.get_handler(name)
        result = await handler(**arguments)  # ← FIXED: No db_session parameter
        return result


# Global registry instance
function_registry = FunctionRegistry()


def register_function(name: str, spec: Dict[str, Any]):
    """Decorator for registering function specs"""
    function_registry.register_function(name, spec)
    return lambda f: f


def register_handler(name: str):
    """Decorator for registering function handlers"""
    def decorator(func: Callable):
        function_registry.register_handler(name, func)
        return func
    return decorator