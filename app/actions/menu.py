"""Menu action handlers for restaurant management"""
from sqlalchemy.orm import Session
from app.models import Restaurant, MenuGroup, MenuItem
from app.function_registry import register_function, register_handler
from app.utils import format_price, parse_price


# ============================================================================
# FUNCTION 5: Create Menu Group
# ============================================================================

register_function(
    "create_menu_group",
    {
        "description": "Create a new menu group/category (e.g., Appetizers, Main Courses, Desserts)",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the menu group"
                }
            },
            "required": ["restaurant_id", "name"]
        }
    }
)


@register_handler("create_menu_group")
async def handle_create_menu_group(
    db: Session,
    restaurant_id: int,
    name: str
) -> str:
    """Create a new menu group"""
    if not name or not name.strip():
        return "Menu group name cannot be empty"
    
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return f"Restaurant with ID {restaurant_id} not found"
    
    # Check if group already exists
    existing = db.query(MenuGroup).filter(
        MenuGroup.restaurant_id == restaurant_id,
        MenuGroup.name == name.strip()
    ).first()
    
    if existing:
        return f"Menu group '{name}' already exists for {restaurant.name}"
    
    # Create new group
    new_group = MenuGroup(
        restaurant_id=restaurant_id,
        name=name.strip()
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    return f"Successfully created menu group '{new_group.name}' (ID: {new_group.id}) for {restaurant.name}"


# ============================================================================
# FUNCTION 6: Create Menu Item
# ============================================================================

register_function(
    "create_menu_item",
    {
        "description": "Create a new menu item with name, description, price, and optional group",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the menu item"
                },
                "price": {
                    "type": "number",
                    "description": "Price in dollars (e.g., 12.99)"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the menu item"
                },
                "group_name": {
                    "type": "string",
                    "description": "Name of the menu group to add this item to (optional)"
                }
            },
            "required": ["restaurant_id", "name", "price"]
        }
    }
)


@register_handler("create_menu_item")
async def handle_create_menu_item(
    db: Session,
    restaurant_id: int,
    name: str,
    price: float,
    description: str = None,
    group_name: str = None
) -> str:
    """Create a new menu item"""
    if not name or not name.strip():
        return "Menu item name cannot be empty"
    
    if price < 0:
        return "Price must be a positive number"
    
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return f"Restaurant with ID {restaurant_id} not found"
    
    # Convert price to cents
    price_cents = int(price * 100)
    
    # Find group if specified
    group_id = None
    if group_name:
        group = db.query(MenuGroup).filter(
            MenuGroup.restaurant_id == restaurant_id,
            MenuGroup.name == group_name.strip()
        ).first()
        if group:
            group_id = group.id
        else:
            return f"Menu group '{group_name}' not found. Please create it first or omit the group."
    
    # Create new item
    new_item = MenuItem(
        restaurant_id=restaurant_id,
        group_id=group_id,
        name=name.strip(),
        description=description.strip() if description else None,
        price=price_cents,
        tags=[]
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    group_text = f" in group '{group_name}'" if group_name else ""
    return f"Successfully created menu item '{new_item.name}' at {format_price(new_item.price)}{group_text} for {restaurant.name}"


# ============================================================================
# FUNCTION 7: Update Menu Item Price
# ============================================================================

register_function(
    "update_menu_item_price",
    {
        "description": "Update the price of an existing menu item",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item to update"
                },
                "new_price": {
                    "type": "number",
                    "description": "New price in dollars (e.g., 15.99)"
                }
            },
            "required": ["restaurant_id", "item_name", "new_price"]
        }
    }
)


@register_handler("update_menu_item_price")
async def handle_update_menu_item_price(
    db: Session,
    restaurant_id: int,
    item_name: str,
    new_price: float
) -> str:
    """Update menu item price"""
    if new_price < 0:
        return "Price must be a positive number"
    
    # Find the menu item
    item = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.name == item_name.strip()
    ).first()
    
    if not item:
        # List available items to help user
        items = db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id
        ).limit(5).all()
        
        if items:
            item_names = ", ".join([i.name for i in items])
            return f"Menu item '{item_name}' not found. Available items include: {item_names}"
        else:
            return f"Menu item '{item_name}' not found and no items exist yet."
    
    # Update price
    old_price = item.price
    new_price_cents = int(new_price * 100)
    item.price = new_price_cents
    db.commit()
    
    return f"Successfully updated '{item.name}' price from {format_price(old_price)} to {format_price(new_price_cents)}"


# ============================================================================
# FUNCTION 8: Toggle Menu Item Tag
# ============================================================================

register_function(
    "toggle_menu_item_tag",
    {
        "description": "Add or remove a tag from a menu item (e.g., 'vegetarian', 'spicy', 'gluten-free')",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "The restaurant ID"
                },
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item"
                },
                "tag": {
                    "type": "string",
                    "description": "Tag to add or remove (e.g., 'vegetarian', 'spicy')"
                }
            },
            "required": ["restaurant_id", "item_name", "tag"]
        }
    }
)


@register_handler("toggle_menu_item_tag")
async def handle_toggle_menu_item_tag(
    db: Session,
    restaurant_id: int,
    item_name: str,
    tag: str
) -> str:
    """Toggle a tag on a menu item"""
    if not tag or not tag.strip():
        return "Tag cannot be empty"
    
    # Find the menu item
    item = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.name == item_name.strip()
    ).first()
    
    if not item:
        return f"Menu item '{item_name}' not found"
    
    # Get current tags
    current_tags = item.tags or []
    tag_lower = tag.strip().lower()
    
    # Toggle tag
    if tag_lower in current_tags:
        current_tags.remove(tag_lower)
        action = "removed"
    else:
        current_tags.append(tag_lower)
        action = "added"
    
    item.tags = current_tags
    db.commit()
    
    tags_str = ", ".join(current_tags) if current_tags else "none"
    return f"Successfully {action} tag '{tag_lower}' for '{item.name}'. Current tags: {tags_str}"
