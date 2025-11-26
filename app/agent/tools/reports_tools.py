"""Reports and analytics tools"""
from app.agent.function_registry import register_function, register_handler
from app.utils import backend_client


# ============================================================================
# FUNCTION: Get Today's Metrics
# ============================================================================

register_function(
    "get_today_metrics",
    {
        "description": "Get today's sales metrics (total sales, dine-in, takeout)",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_today_metrics")
async def handle_get_today_metrics(restaurant_id: int) -> str:
    """Get today's metrics"""
    response = await backend_client.post("/dashboard/today-metrics", {"r_id": restaurant_id})
    
    if response.get("status") == "200" or "today_sales" in response:
        data = response
        return f"""📊 Today's Metrics:
Total Sales: {data.get('today_sales', 0)} orders
Dine-in: {data.get('total_dine_in', 0)} orders (₹{data.get('total_dine_in_amount', 0)})
Takeout: {data.get('total_takeout', 0)} orders (₹{data.get('total_takeout_amount', 0)})
Total Amount: ₹{data.get('today_sales_amount', 0)}
"""
    else:
        return "❌ Failed to fetch metrics"


# ============================================================================
# FUNCTION: Get Sales Trends
# ============================================================================

register_function(
    "get_sales_trends",
    {
        "description": "Get sales trends for last 30 days",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"}
            },
            "required": ["restaurant_id"]
        }
    }
)

@register_handler("get_sales_trends")
async def handle_get_sales_trends(restaurant_id: int) -> str:
    """Get sales trends"""
    response = await backend_client.post("/dashboard/sales-trends", {"r_id": restaurant_id})
    
    if response.get("status") == "200" or "sales_trends" in response:
        trends = response.get("sales_trends", [])
        if not trends:
            return "No sales data available"
        
        # Show last 7 days
        recent = trends[-7:] if len(trends) >= 7 else trends
        trend_text = "\n".join([
            f"{t['day'][:3]} {t['date']}: {t['daily_sales']} orders"
            for t in recent
        ])
        return f"📈 Sales Trends (Last 7 Days):\n{trend_text}"
    else:
        return "❌ Failed to fetch trends"


# ============================================================================
# FUNCTION: Generate Sales Report
# ============================================================================

register_function(
    "generate_sales_report",
    {
        "description": "Generate downloadable sales report (CSV/PDF)",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "dine_in": {"type": "boolean", "description": "Include dine-in orders"},
                "pay_mode": {"type": "string", "description": "Payment mode filter"}
            },
            "required": ["restaurant_id", "start_date", "end_date"]
        }
    }
)

@register_handler("generate_sales_report")
async def handle_generate_sales_report(
    restaurant_id: int,
    start_date: str,
    end_date: str,
    dine_in: bool = True,
    pay_mode: str = "all"
) -> str:
    """Generate sales report"""
    response = await backend_client.post("/reports/download/csv", {
        "start_date": start_date,
        "end_date": end_date,
        "dine_in": dine_in,
        "pay_mode": pay_mode
    })
    
    if response.get("file_path"):
        return f"✅ Report generated! Download from: {response.get('file_path')}"
    else:
        return "✅ Report generation initiated. Check your backend for the file."