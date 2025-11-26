"""Utility functions"""
from typing import Dict, Any, Optional


def format_price(cents: int) -> str:
    """
    Format price in cents to dollar string
    
    Args:
        cents: Price in cents
        
    Returns:
        Formatted price string (e.g., "$12.99")
    """
    dollars = cents / 100
    return f"${dollars:.2f}"


def parse_price(price_str: str) -> Optional[int]:
    """
    Parse price string to cents
    
    Args:
        price_str: Price string (e.g., "$12.99" or "12.99")
        
    Returns:
        Price in cents or None if invalid
    """
    try:
        # Remove $ and whitespace
        clean = price_str.strip().replace("$", "")
        # Convert to float then to cents
        dollars = float(clean)
        return int(dollars * 100)
    except (ValueError, AttributeError):
        return None


def format_business_hours(hours: Dict[str, str]) -> str:
    """
    Format business hours dict to readable string
    
    Args:
        hours: Dict with day: hours mapping
        
    Returns:
        Formatted string
    """
    if not hours:
        return "Not set"
    
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    lines = []
    for day in days_order:
        if day in hours:
            lines.append(f"{day.capitalize()}: {hours[day]}")
    
    return "\n".join(lines) if lines else "Not set"


def validate_business_hours_format(hours_str: str) -> bool:
    """
    Validate business hours format (e.g., "9:00-17:00")
    
    Args:
        hours_str: Hours string to validate
        
    Returns:
        True if valid format
    """
    try:
        if "-" not in hours_str:
            return False
        start, end = hours_str.split("-")
        # Basic validation of time format
        for time in [start.strip(), end.strip()]:
            parts = time.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return False
        return True
    except:
        return False