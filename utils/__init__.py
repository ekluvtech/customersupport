"""Utility Functions"""

from utils.validation import (
    validate_email,
    validate_order_id,
    validate_ticket_id,
    validate_date,
    validate_required_fields,
    sanitize_string,
    validate_status,
    validate_pagination_params
)

from utils.formatting import (
    format_ticket_summary,
    format_order_summary,
    format_datetime,
    format_date,
    format_currency,
    format_list,
    format_json,
    truncate_text,
    format_error_message,
    format_tool_result
)

from utils.error_handler import (
    SupportAgentError,
    IntegrationError,
    ValidationError,
    ConfigurationError,
    handle_integration_error,
    handle_validation_error,
    retry_on_failure,
    safe_execute
)

from utils.logger import (
    setup_logger,
    get_logger,
    LoggerMixin
)

from utils.helpers import (
    get_env_var,
    ensure_directory,
    merge_dicts,
    filter_dict,
    exclude_dict_keys,
    deep_get,
    chunk_list,
    sanitize_filename
)

__all__ = [
    # Validation
    "validate_email",
    "validate_order_id",
    "validate_ticket_id",
    "validate_date",
    "validate_required_fields",
    "sanitize_string",
    "validate_status",
    "validate_pagination_params",
    # Formatting
    "format_ticket_summary",
    "format_order_summary",
    "format_datetime",
    "format_date",
    "format_currency",
    "format_list",
    "format_json",
    "truncate_text",
    "format_error_message",
    "format_tool_result",
    # Error handling
    "SupportAgentError",
    "IntegrationError",
    "ValidationError",
    "ConfigurationError",
    "handle_integration_error",
    "handle_validation_error",
    "retry_on_failure",
    "safe_execute",
    # Logging
    "setup_logger",
    "get_logger",
    "LoggerMixin",
    # Helpers
    "get_env_var",
    "ensure_directory",
    "merge_dicts",
    "filter_dict",
    "exclude_dict_keys",
    "deep_get",
    "chunk_list",
    "sanitize_filename"
]

