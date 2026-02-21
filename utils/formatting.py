"""Formatting utilities"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json


def format_ticket_summary(ticket: Dict[str, Any]) -> str:
    """Format a Zendesk ticket for display"""
    ticket_id = ticket.get("id", "N/A")
    subject = ticket.get("subject", "No subject")
    status = ticket.get("status", "unknown")
    priority = ticket.get("priority", "normal")
    created_at = ticket.get("created_at", "")
    
    summary = f"Ticket #{ticket_id}: {subject}\n"
    summary += f"Status: {status.title()}, Priority: {priority.title()}\n"
    
    if created_at:
        summary += f"Created: {format_datetime(created_at)}\n"
    
    return summary


def format_order_summary(order: Dict[str, Any]) -> str:
    """Format an order for display"""
    order_id = order.get("order_id", "N/A")
    status = order.get("status", "unknown")
    total = order.get("total_amount", 0)
    customer_email = order.get("customer_email", "N/A")
    
    summary = f"Order #{order_id}\n"
    summary += f"Status: {status.title()}\n"
    summary += f"Total: ${total:.2f}\n"
    summary += f"Customer: {customer_email}\n"
    
    if order.get("tracking_number"):
        summary += f"Tracking: {order['tracking_number']}\n"
    
    if order.get("estimated_delivery"):
        summary += f"Estimated Delivery: {format_date(order['estimated_delivery'])}\n"
    
    return summary


def format_datetime(dt_string: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime string"""
    try:
        # Try parsing ISO format
        if 'T' in dt_string:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        
        return dt.strftime(format)
    except (ValueError, AttributeError):
        return dt_string


def format_date(date_string: str, format: str = "%Y-%m-%d") -> str:
    """Format date string"""
    try:
        if isinstance(date_string, str):
            dt = datetime.strptime(date_string, "%Y-%m-%d")
            return dt.strftime(format)
        return str(date_string)
    except (ValueError, AttributeError):
        return str(date_string)


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_list(items: List[Any], separator: str = ", ", max_items: Optional[int] = None) -> str:
    """Format a list of items as a string"""
    if max_items and len(items) > max_items:
        displayed = items[:max_items]
        return separator.join(str(item) for item in displayed) + f" ... and {len(items) - max_items} more"
    return separator.join(str(item) for item in items)


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON string"""
    try:
        return json.dumps(data, indent=indent, default=str)
    except (TypeError, ValueError):
        return str(data)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_error_message(error: Exception, include_traceback: bool = False) -> str:
    """Format error message for user display"""
    message = f"Error: {str(error)}"
    
    if include_traceback:
        import traceback
        message += f"\n\nTraceback:\n{traceback.format_exc()}"
    
    return message


def format_tool_result(tool_name: str, result: Any, success: bool = True) -> Dict[str, Any]:
    """Format tool execution result"""
    return {
        "tool": tool_name,
        "success": success,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

