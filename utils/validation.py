"""Validation utilities"""

import re
from typing import Any, Optional, List, Dict
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_order_id(order_id: str) -> bool:
    """Validate order ID format (alphanumeric, typically 5-20 characters)"""
    if not order_id or not isinstance(order_id, str):
        return False
    
    # Allow alphanumeric and common separators
    pattern = r'^[A-Z0-9\-_]+$'
    return bool(re.match(pattern, order_id.upper())) and 3 <= len(order_id) <= 50


def validate_ticket_id(ticket_id: Any) -> bool:
    """Validate Zendesk ticket ID (numeric)"""
    if isinstance(ticket_id, int):
        return ticket_id > 0
    if isinstance(ticket_id, str):
        return ticket_id.isdigit() and int(ticket_id) > 0
    return False


def validate_date(date_string: str, format: str = "%Y-%m-%d") -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_string, format)
        return True
    except (ValueError, TypeError):
        return False


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple:
    """
    Validate that all required fields are present in data
    
    Returns:
        (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def sanitize_string(value: Any, max_length: Optional[int] = None) -> str:
    """Sanitize string input"""
    if value is None:
        return ""
    
    string_value = str(value).strip()
    
    if max_length and len(string_value) > max_length:
        string_value = string_value[:max_length]
    
    return string_value


def validate_status(status: str, allowed_statuses: List[str]) -> bool:
    """Validate status value against allowed list"""
    return status.lower() in [s.lower() for s in allowed_statuses]


def validate_pagination_params(page: Optional[int] = None, limit: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """Validate pagination parameters"""
    if page is not None and (not isinstance(page, int) or page < 1):
        return False, "Page must be a positive integer"
    
    if limit is not None:
        if not isinstance(limit, int) or limit < 1:
            return False, "Limit must be a positive integer"
        if limit > 1000:
            return False, "Limit cannot exceed 1000"
    
    return True, None

