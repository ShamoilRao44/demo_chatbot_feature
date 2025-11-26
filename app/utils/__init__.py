"""HTTP client for communicating with main backend"""
import httpx
from typing import Dict, Any, Optional
from app.config import get_settings

settings = get_settings()


class BackendClient:
    """Client for calling main restaurant backend APIs"""
    
    def __init__(self):
        self.base_url = settings.backend_url
        self.timeout = 30.0
    
    async def call(
        self,
        endpoint: str,
        method: str = "POST",
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP call to main backend
        
        Args:
            endpoint: API endpoint (e.g., "/groups/create")
            method: HTTP method (GET, POST, PUT, DELETE)
            json_data: JSON body for POST/PUT
            params: Query parameters
            
        Returns:
            Response JSON
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.base_url}{endpoint}"
            
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {
                    "status": "error",
                    "msg": f"Backend API error: {str(e)}"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "msg": f"Error calling backend: {str(e)}"
                }
    
    # Convenience methods for common operations
    
    async def get(self, endpoint: str, **params) -> Dict[str, Any]:
        """GET request"""
        return await self.call(endpoint, "GET", params=params)
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request"""
        return await self.call(endpoint, "POST", json_data=data)
    
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT request"""
        return await self.call(endpoint, "PUT", json_data=data)
    
    async def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """DELETE request"""
        return await self.call(endpoint, "DELETE", json_data=data)


# Global backend client instance
backend_client = BackendClient()

