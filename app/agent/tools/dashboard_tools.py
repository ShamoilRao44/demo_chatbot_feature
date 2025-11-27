"""Dashboard tools for restaurant management - CORRECTED FOR ACTUAL BACKEND"""
from typing import Dict, Any
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION 1: Get Restaurant Info (PLACEHOLDER - no direct API)
# ============================================================================

register_function(
    "get_restaurant_info",
    {
        "description": "Get current restaurant information including prep time, address, hours, and status",
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

@register_handler("get_restaurant_info")
async def handle_get_restaurant_info(restaurant_id: int) -> str:
    """Get restaurant information - No direct API, return message"""
    return "ℹ️ Restaurant info can be updated using customize restaurant function. Use specific functions to change prep time, address, or hours."


# ============================================================================
# FUNCTION 2: Update Prep Time
# ACTUAL API: POST /customize/restaurant with est_prep_time field
# ============================================================================

register_function(
    "update_prep_time",
    {
        "description": "Update estimated preparation time for orders",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "Restaurant ID"
                },
                "prep_time_minutes": {
                    "type": "integer",
                    "description": "Preparation time in minutes"
                }
            },
            "required": ["restaurant_id", "prep_time_minutes"]
        }
    }
)

@register_handler("update_prep_time")
async def handle_update_prep_time(restaurant_id: int, prep_time_minutes: int) -> str:
    """Update preparation time using /customize/restaurant"""
    response = await backend_client.post("/customize/restaurant", {
        "r_id": restaurant_id,
        "est_prep_time": prep_time_minutes  # ✅ CORRECT FIELD NAME
    })
    
    if response.get("status") == "200":
        return f"✅ Successfully updated prep time to {prep_time_minutes} minutes"
    else:
        return f"❌ Failed to update prep time: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION 3: Update Business Hours
# ACTUAL API: POST /customize/restaurant with opening_hours field
# ============================================================================

register_function(
    "update_business_hours",
    {
        "description": "Update opening and closing hours for specific day",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "Restaurant ID"
                },
                "day_of_week": {
                    "type": "integer",
                    "description": "Day (0=Monday, 6=Sunday)"
                },
                "opening_time": {
                    "type": "string",
                    "description": "Opening time (HH:MM format)"
                },
                "closing_time": {
                    "type": "string",
                    "description": "Closing time (HH:MM format)"
                }
            },
            "required": ["restaurant_id", "day_of_week", "opening_time", "closing_time"]
        }
    }
)

@register_handler("update_business_hours")
async def handle_update_business_hours(
    restaurant_id: int,
    day_of_week: int,
    opening_time: str,
    closing_time: str
) -> str:
    """Update business hours using /customize/restaurant"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = days[day_of_week] if 0 <= day_of_week <= 6 else "Unknown"
    
    response = await backend_client.post("/customize/restaurant", {
        "r_id": restaurant_id,
        "opening_hours": [{  # ✅ CORRECT FIELD NAME
            "day_of_week": day_of_week,
            "opening_time": opening_time,
            "closing_time": closing_time
        }]
    })
    
    if response.get("status") == "200":
        return f"✅ Successfully updated {day_name} hours to {opening_time}-{closing_time}"
    else:
        return f"❌ Failed to update hours: {response.get('msg', 'Unknown error')}"


# ============================================================================
# FUNCTION 4: Pause Restaurant (NO API AVAILABLE)
# ============================================================================

register_function(
    "pause_restaurant",
    {
        "description": "Pause restaurant to stop accepting new orders",
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

@register_handler("pause_restaurant")
async def handle_pause_restaurant(restaurant_id: int) -> str:
    """Pause restaurant - API not available in backend"""
    return "❌ Pause restaurant functionality is not available in the current backend. Please contact support to add this feature."


# ============================================================================
# FUNCTION 5: Unpause Restaurant (NO API AVAILABLE)
# ============================================================================

register_function(
    "unpause_restaurant",
    {
        "description": "Unpause restaurant to resume accepting orders",
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

@register_handler("unpause_restaurant")
async def handle_unpause_restaurant(restaurant_id: int) -> str:
    """Unpause restaurant - API not available in backend"""
    return "❌ Unpause restaurant functionality is not available in the current backend. Please contact support to add this feature."


# ============================================================================
# FUNCTION 6: Update Restaurant Address
# ACTUAL API: POST /customize/restaurant with address field
# ============================================================================

register_function(
    "update_restaurant_address",
    {
        "description": "Update restaurant's physical address",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "Restaurant ID"
                },
                "address": {
                    "type": "string",
                    "description": "New address"
                }
            },
            "required": ["restaurant_id", "address"]
        }
    }
)

@register_handler("update_restaurant_address")
async def handle_update_restaurant_address(restaurant_id: int, address: str) -> str:
    """Update restaurant address using /customize/restaurant"""
    response = await backend_client.post("/customize/restaurant", {
        "r_id": restaurant_id,
        "address": address  # ✅ CORRECT FIELD NAME
    })
    
    if response.get("status") == "200":
        return f"✅ Successfully updated address to: {address}"
    else:
        return f"❌ Failed to update address: {response.get('msg', 'Unknown error')}"