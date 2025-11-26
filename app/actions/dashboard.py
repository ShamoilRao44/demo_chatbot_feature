"""Dashboard action handlers for restaurant management"""
from sqlalchemy.orm import Session
from app.models import Restaurant
from app.agent.function_registry import register_function, register_handler
from app.utils import validate_business_hours_format


# ============================================================================
# FUNCTION 1: Update Business Hours
# ============================================================================

register_function(
    "update_business_hours",
    {
        "description": "Update the business hours for a specific day of the week",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "day": {
                    "type": "string",
                    "description": "Day of the week (monday, tuesday, etc.)",
                    "enum": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                },
                "hours": {
                    "type": "string",
                    "description": "Business hours in format HH:MM-HH:MM (e.g., 09:00-17:00)"
                }
            },
            "required": ["restaurant_id", "day", "hours"]
        }
    }
)


@register_handler("update_business_hours")
async def handle_update_business_hours(
    db: Session,
    restaurant_id: int,
    day: str,
    hours: str
) -> str:
    """Update business hours for a specific day"""
    # Validate hours format
    if not validate_business_hours_format(hours):
        return f"Invalid hours format. Please use HH:MM-HH:MM format (e.g., 09:00-17:00)"
    
    # Get restaurant
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return f"Restaurant with ID {restaurant_id} not found"
    
    # Update business hours
    current_hours = restaurant.business_hours or {}
    current_hours[day.lower()] = hours
    restaurant.business_hours = current_hours
    
    db.commit()
    
    return f"Successfully updated {day.capitalize()} hours to {hours} for {restaurant.name}"


# ============================================================================
# FUNCTION 2: Update Prep Time
# ============================================================================

register_function(
    "update_prep_time",
    {
        "description": "Update the preparation time in minutes for the restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
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
async def handle_update_prep_time(
    db: Session,
    restaurant_id: int,
    prep_time_minutes: int
) -> str:
    """Update restaurant preparation time"""
    if prep_time_minutes < 0:
        return "Preparation time must be a positive number"
    
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return f"Restaurant with ID {restaurant_id} not found"
    
    old_time = restaurant.prep_time_minutes
    restaurant.prep_time_minutes = prep_time_minutes
    db.commit()
    
    return f"Successfully updated prep time from {old_time} minutes to {prep_time_minutes} minutes for {restaurant.name}"


# ============================================================================
# FUNCTION 3: Set Restaurant Pause State
# ============================================================================

register_function(
    "set_restaurant_pause_state",
    {
        "description": "Pause or unpause the restaurant (stops accepting orders when paused)",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "is_paused": {
                    "type": "boolean",
                    "description": "True to pause, False to unpause"
                }
            },
            "required": ["restaurant_id", "is_paused"]
        }
    }
)


@register_handler("set_restaurant_pause_state")
async def handle_set_restaurant_pause_state(
    db: Session,
    restaurant_id: int,
    is_paused: bool
) -> str:
    """Pause or unpause restaurant"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return f"Restaurant with ID {restaurant_id} not found"
    
    restaurant.is_paused = is_paused
    db.commit()
    
    status = "paused" if is_paused else "unpaused"
    return f"Successfully {status} {restaurant.name}. {'Orders are now stopped.' if is_paused else 'Orders are now active.'}"


# ============================================================================
# FUNCTION 4: Update Restaurant Address
# ============================================================================

register_function(
    "update_restaurant_address",
    {
        "description": "Update the restaurant's physical address",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "address": {
                    "type": "string",
                    "description": "The new address"
                }
            },
            "required": ["restaurant_id", "address"]
        }
    }
)


@register_handler("update_restaurant_address")
async def handle_update_restaurant_address(
    db: Session,
    restaurant_id: int,
    address: str
) -> str:
    """Update restaurant address"""
    if not address or not address.strip():
        return "Address cannot be empty"
    
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return f"Restaurant with ID {restaurant_id} not found"
    
    old_address = restaurant.address or "Not set"
    restaurant.address = address.strip()
    db.commit()
    
    return f"Successfully updated address for {restaurant.name} from '{old_address}' to '{address}'"