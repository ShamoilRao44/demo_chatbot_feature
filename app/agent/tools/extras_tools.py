"""Extras and labels management tools"""
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION: Get Labels
# ============================================================================

register_function(
    "get_labels",
    {
        "description": "Get all available labels (veg, non-veg, spicy, etc.)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
)

@register_handler("get_labels")
async def handle_get_labels() -> str:
    """Get all labels"""
    response = await backend_client.get("/labels/")
    
    if response.get("status") == "200":
        labels = response.get("data", [])
        if not labels:
            return "No labels found"
        
        label_list = "\n".join([f"- {l.get('name')} (ID: {l.get('id')})" for l in labels])
        return f"🏷️ Available Labels:\n{label_list}"
    else:
        return "❌ Failed to fetch labels"


# ============================================================================
# FUNCTION: Create Label
# ============================================================================

register_function(
    "create_label",
    {
        "description": "Create a new label (veg, spicy, gluten-free, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Label name"}
            },
            "required": ["name"]
        }
    }
)

@register_handler("create_label")
async def handle_create_label(name: str) -> str:
    """Create label"""
    response = await backend_client.post("/labels/create", {"name": name})
    
    if response.get("status") == "200":
        return f"✅ Created label '{name}'"
    else:
        return f"❌ Failed to create label: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION: Get Extras
# ============================================================================

register_function(
    "get_extras",
    {
        "description": "Get all extras/addons for a restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_extras")
async def handle_get_extras(restaurant_id: int) -> str:
    """Get extras"""
    response = await backend_client.post("/extras/", {"r_id": restaurant_id})
    
    if response.get("status") == "200":
        extras = response.get("data", [])
        if not extras:
            return "No extras found"
        
        extra_list = "\n".join([
            f"- {e.get('name')} (₹{e.get('price')}) - ID: {e.get('id')}"
            for e in extras
        ])
        return f"🧀 Available Extras:\n{extra_list}"
    else:
        return "❌ Failed to fetch extras"


# ============================================================================
# FUNCTION: Create Extra
# ============================================================================

register_function(
    "create_extra",
    {
        "description": "Create a new extra/addon (cheese, sauce, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "name": {"type": "string", "description": "Extra name"},
                "price": {"type": "number", "description": "Extra price"}
            },
            "required": ["restaurant_id", "name", "price"]
        }
    }
)

@register_handler("create_extra")
async def handle_create_extra(restaurant_id: int, name: str, price: float) -> str:
    """Create extra"""
    response = await backend_client.post("/extras/create", {
        "r_id": restaurant_id,
        "name": name,
        "price": price
    })
    
    if response.get("status") == "200":
        return f"✅ Created extra '{name}' at ₹{price}"
    else:
        return f"❌ Failed to create extra: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION: Delete Extra
# ============================================================================

register_function(
    "delete_extra",
    {
        "description": "Delete an extra/addon",
        "parameters": {
            "type": "object",
            "properties": {
                "extra_id": {"type": "integer"}
            },
            "required": ["extra_id"]
        }
    }
)

@register_handler("delete_extra")
async def handle_delete_extra(extra_id: int) -> str:
    """Delete extra"""
    response = await backend_client.put(f"/extras/delete/{extra_id}", {})
    
    if response.get("status") == "200":
        return f"✅ Deleted extra (ID: {extra_id})"
    else:
        return f"❌ Failed to delete extra: {response.get('msg', 'Unknown error')}"