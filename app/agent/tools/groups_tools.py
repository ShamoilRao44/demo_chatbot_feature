"""Group/Category management tools"""
from typing import Dict, Any
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION 7: Get Menu Groups
# ============================================================================

register_function(
    "get_menu_groups",
    {
        "description": "Get all menu groups/categories for the restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "Restaurant ID"
                }
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_menu_groups")
async def handle_get_menu_groups(restaurant_id: int) -> str:
    """Get all menu groups"""
    response = await backend_client.post("/groups/", {"r_id": restaurant_id})
    
    if response.get("status") == "200":
        groups = response.get("data", {}).get("groups", [])
        if not groups:
            return "No menu groups found. Create one first!"
        
        group_list = "\n".join([
            f"- {g['gname']} (ID: {g['g_id']})"
            for g in groups
        ])
        return f"📋 Menu Groups:\n{group_list}"
    else:
        return f"❌ Failed to fetch groups: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION 8: Create Menu Group
# ============================================================================

register_function(
    "create_menu_group",
    {
        "description": "Create a new menu group/category",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "Restaurant ID"
                },
                "name": {
                    "type": "string",
                    "description": "Group name (e.g., Appetizers, Main Course, Breads)"
                },
                "icon": {
                    "type": "integer",
                    "description": "Icon ID (default: 1)",
                    "default": 1
                }
            },
            "required": ["restaurant_id", "name"]
        }
    }
)

@register_handler("create_menu_group")
async def handle_create_menu_group(restaurant_id: int, name: str, icon: int = 1) -> str:
    """Create menu group"""
    response = await backend_client.post("/groups/create", {
        "r_id": restaurant_id,
        "name": name,
        "g_icon": icon
    })
    
    if response.get("status") == "200":
        group_data = response.get("data", {}).get("group", {})
        return f"✅ Created menu group '{name}' (ID: {group_data.get('g_id')})"
    else:
        return f"❌ Failed to create group: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION 9: Delete Menu Group
# ============================================================================

register_function(
    "delete_menu_group",
    {
        "description": "Delete a menu group/category",
        "parameters": {
            "type": "object",
            "properties": {
                "group_id": {
                    "type": "integer",
                    "description": "Group ID to delete"
                }
            },
            "required": ["group_id"]
        }
    }
)

@register_handler("delete_menu_group")
async def handle_delete_menu_group(group_id: int) -> str:
    """Delete menu group"""
    response = await backend_client.delete("/groups/delete", {"g_id": group_id})
    
    if response.get("status") == "200":
        return f"✅ Successfully deleted group (ID: {group_id})"
    else:
        return f"❌ Failed to delete group: {response.get('msg', 'Cannot delete if items exist')}"