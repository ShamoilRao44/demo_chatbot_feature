"""Order management tools"""
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION: Get All Orders
# ============================================================================

register_function(
    "get_orders",
    {
        "description": "Get all pending orders for the restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_orders")
async def handle_get_orders(restaurant_id: int) -> str:
    """Get all orders"""
    response = await backend_client.post("/orders/", {"r_id": restaurant_id})
    
    if response.get("status") == "200":
        orders = response.get("data", [])
        if not orders:
            return "No pending orders"
        
        order_summary = f"📋 {len(orders)} Pending Orders:\n\n"
        for order in orders[:10]:  # Show first 10
            items_count = len(order.get("items", []))
            dine_type = "Dine-in" if order.get("dine_in") else "Takeout"
            order_summary += f"Order #{order['order_id']} - {dine_type}\n"
            order_summary += f"  {items_count} items, ₹{order['amount']}\n"
            order_summary += f"  Customer: {order.get('user_details', {}).get('name')}\n\n"
        
        return order_summary
    else:
        return f"❌ {response.get('msg', 'Failed to fetch orders')}"


# ============================================================================
# FUNCTION: Get Completed Orders
# ============================================================================

register_function(
    "get_completed_orders",
    {
        "description": "Get all completed/past orders",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_completed_orders")
async def handle_get_completed_orders(restaurant_id: int) -> str:
    """Get completed orders"""
    response = await backend_client.post("/orders/completed-orders", {"r_id": restaurant_id})
    
    if response.get("status") == "200":
        orders = response.get("data", [])
        if not orders:
            return "No completed orders"
        
        return f"✅ {len(orders)} completed orders found. Recent orders displayed on your dashboard."
    else:
        return f"❌ {response.get('msg', 'Failed to fetch completed orders')}"


# ============================================================================
# FUNCTION: Cancel Order
# ============================================================================

register_function(
    "cancel_order",
    {
        "description": "Cancel a pending order",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID to cancel"}
            },
            "required": ["order_id"]
        }
    }
)

@register_handler("cancel_order")
async def handle_cancel_order(order_id: int) -> str:
    """Cancel order"""
    response = await backend_client.delete("/orders/delete", {"o_id": order_id})
    
    if response.get("status") == "200":
        return f"✅ Order #{order_id} cancelled successfully"
    else:
        return f"❌ {response.get('msg', 'Failed to cancel order')}"


# ============================================================================
# FUNCTION: Complete Order
# ============================================================================

register_function(
    "complete_order",
    {
        "description": "Mark an order as completed",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"}
            },
            "required": ["order_id"]
        }
    }
)

@register_handler("complete_order")
async def handle_complete_order(order_id: int) -> str:
    """Complete order"""
    response = await backend_client.post("/orders/complete", {
        "o_id": order_id
    })
    
    if response.get("status") == "200":
        return f"✅ Order #{order_id} completed and moved to history"
    else:
        return f"❌ {response.get('msg', 'Failed to complete order')}"