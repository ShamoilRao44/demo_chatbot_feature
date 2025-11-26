"""Menu item management tools"""
from typing import Dict, Any, Optional
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION 10: Create Menu Item (Default Price)
# ============================================================================

register_function(
    "create_menu_item",
    {
        "description": "Create a new menu item with default price",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "group_id": {"type": "integer", "description": "Menu group ID"},
                "name": {"type": "string", "description": "Item name"},
                "price": {"type": "number", "description": "Price in rupees/dollars"},
                "desc": {"type": "string", "description": "Description (optional)"},
                "image": {"type": "string", "description": "Image URL (optional)"},
                "ordertype": {"type": "integer", "description": "Order type (default: 0)"},
                "labels": {"type": "array", "description": "Label IDs (optional)"},
                "extras_list": {"type": "array", "description": "Extra IDs (optional)"}
            },
            "required": ["restaurant_id", "group_id", "name", "price"]
        }
    }
)

@register_handler("create_menu_item")
async def handle_create_menu_item(
    restaurant_id: int,
    group_id: int,
    name: str,
    price: float,
    desc: str = "",
    image: str = "",
    ordertype: int = 0,
    labels: list = None,
    extras_list: list = None
) -> str:
    """Create menu item"""
    response = await backend_client.post("/menu/create", {
        "r_id": restaurant_id,
        "g_id": group_id,
        "name": name,
        "def_price": price,
        "desc": desc,
        "image": image,
        "ordertype": ordertype,
        "labels": labels or [],
        "extras_list": extras_list or []
    })
    
    if response.get("status") == "200":
        item_data = response.get("data", {}).get("item", {})
        return f"✅ Created menu item '{name}' at ₹{price} (ID: {item_data.get('id')})"
    else:
        return f"❌ Failed to create item: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION 11: Update Menu Item
# ============================================================================

register_function(
    "update_menu_item",
    {
        "description": "Update menu item details (name, price, description, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {"type": "integer"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "desc": {"type": "string"},
                "enable": {"type": "boolean"},
                "sold_out": {"type": "boolean"}
            },
            "required": ["item_id"]
        }
    }
)

@register_handler("update_menu_item")
async def handle_update_menu_item(
    item_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    desc: Optional[str] = None,
    enable: Optional[bool] = None,
    sold_out: Optional[bool] = None
) -> str:
    """Update menu item"""
    update_data = {"id": item_id}
    if name: update_data["name"] = name
    if price: update_data["def_price"] = price
    if desc: update_data["desc"] = desc
    if enable is not None: update_data["enable"] = enable
    if sold_out is not None: update_data["sold_out"] = sold_out
    
    response = await backend_client.post("/customize/item", update_data)
    
    if response.get("status") == "200":
        return f"✅ Successfully updated item (ID: {item_id})"
    else:
        return f"❌ Failed to update item: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION 12: Get Menu Items
# ============================================================================

register_function(
    "get_menu_items",
    {
        "description": "Get all menu items, optionally filtered by group",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "group_id": {"type": "integer", "description": "Filter by group (optional)"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_menu_items")
async def handle_get_menu_items(restaurant_id: int, group_id: Optional[int] = None) -> str:
    """Get menu items"""
    response = await backend_client.post("/menu/", {
        "r_id": restaurant_id,
        "g_id": group_id
    })
    
    if response.get("status") == "200":
        items = response.get("data", {}).get("items", [])
        if not items:
            return "No menu items found."
        
        item_list = "\n".join([
            f"- {item.get('name')} (₹{item.get('def_price')}) - ID: {item.get('id')}"
            for item in items[:20]  # Limit to 20
        ])
        return f"🍽️ Menu Items:\n{item_list}"
    else:
        return f"❌ Failed to fetch items: {response.get('msg', 'Unknown error')}"