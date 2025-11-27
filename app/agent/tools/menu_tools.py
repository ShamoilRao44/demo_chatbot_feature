"""Menu item management tools - CORRECTED FOR ACTUAL BACKEND"""
from typing import Dict, Any, Optional
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION: Create Menu Item
# ACTUAL API: POST /menu/create/default
# ============================================================================

register_function(
    "create_menu_item",
    {
        "description": "Create a new menu item with default price",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "group_id": {"type": "integer", "description": "Menu group ID (g_id)"},
                "name": {"type": "string", "description": "Item name"},
                "price": {"type": "number", "description": "Price in rupees"},
                "desc": {"type": "string", "description": "Description (optional)"},
                "image": {"type": "string", "description": "Image URL (optional)"},
                "ordertype": {"type": "integer", "description": "Order type: 0=both, 1=dine-in only, 2=takeout only"},
                "labels": {"type": "array", "description": "Label IDs array (optional)"},
                "extras_list": {"type": "array", "description": "Extra IDs array (optional)"}
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
    """Create menu item using /menu/create/default"""
    response = await backend_client.post("/menu/create/default", {
        "r_id": restaurant_id,  # ✅ CORRECT FIELD NAMES
        "g_id": group_id,
        "name": name,
        "def_price": price,  # ✅ def_price not just price
        "desc": desc,
        "image": image,
        "ordertype": ordertype,
        "is_avail": True,  # ✅ Required field
        "labels": labels or [],
        "extras_list": extras_list or []
    })
    
    if response.get("status") == "200":
        item_data = response.get("data", {}).get("item", {})
        return f"✅ Created menu item '{name}' at ₹{price} (ID: {item_data.get('item_id')})"
    else:
        return f"❌ Failed to create item: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION: Update Menu Item
# ACTUAL API: POST /customize/item
# ============================================================================

register_function(
    "update_menu_item",
    {
        "description": "Update menu item details (name, price, description, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {"type": "integer", "description": "Item ID to update"},
                "name": {"type": "string", "description": "New name (optional)"},
                "price": {"type": "number", "description": "New price (optional)"},
                "desc": {"type": "string", "description": "New description (optional)"},
                "enable": {"type": "boolean", "description": "Enable/disable item (optional)"},
                "sold_out": {"type": "boolean", "description": "Mark as sold out (optional)"}
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
    """Update menu item using /customize/item"""
    update_data = {"id": item_id}  # ✅ CORRECT FIELD NAME
    
    if name: update_data["name"] = name
    if price: update_data["def_price"] = price  # ✅ def_price not just price
    if desc: update_data["desc"] = desc
    if enable is not None: update_data["enable"] = enable
    if sold_out is not None: update_data["sold_out"] = sold_out
    
    response = await backend_client.post("/customize/item", update_data)
    
    if response.get("status") == "200":
        return f"✅ Successfully updated item (ID: {item_id})"
    else:
        return f"❌ Failed to update item: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION: Get Menu Items
# ACTUAL API: POST /menu/ or POST /menu/v2
# ============================================================================

register_function(
    "get_menu_items",
    {
        "description": "Get all menu items, optionally filtered by group",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "group_id": {"type": "integer", "description": "Filter by group ID (optional)"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_menu_items")
async def handle_get_menu_items(restaurant_id: int, group_id: Optional[int] = None) -> str:
    """Get menu items using /menu/v2"""
    response = await backend_client.post("/menu/v2", {
        "r_id": restaurant_id  # ✅ CORRECT FIELD NAME
    })
    
    if response.get("status") == "200":
        data = response.get("data", {})
        groups = data.get("groups", [])
        
        if not groups:
            return "No menu items found."
        
        # If group_id specified, filter to that group
        if group_id:
            groups = [g for g in groups if g.get("g_id") == group_id]
            if not groups:
                return f"No items found in group ID {group_id}"
        
        # Build item list
        item_list = []
        for group in groups:
            group_name = group.get("gname", "Unknown")
            items = group.get("items", [])
            for item in items[:10]:  # Limit to 10 per group
                item_list.append(
                    f"- {item.get('name')} (₹{item.get('def_price', 0)}) - Group: {group_name}, ID: {item.get('item_id')}"
                )
        
        if not item_list:
            return "No menu items found."
        
        return f"🍽️ Menu Items:\n" + "\n".join(item_list)
    else:
        return f"❌ Failed to fetch items: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION: Delete Menu Item
# ACTUAL API: DELETE /menu/item/delete/{item_id}
# ============================================================================

register_function(
    "delete_menu_item",
    {
        "description": "Delete a menu item",
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {"type": "integer", "description": "Item ID to delete"}
            },
            "required": ["item_id"]
        }
    }
)

@register_handler("delete_menu_item")
async def handle_delete_menu_item(item_id: int) -> str:
    """Delete menu item using DELETE /menu/item/delete/{item_id}"""
    response = await backend_client.delete(f"/menu/item/delete/{item_id}", {})
    
    if response.get("status") == "200":
        return f"✅ Successfully deleted item (ID: {item_id})"
    else:
        return f"❌ Failed to delete item: {response.get('msg', 'Unknown error')}"