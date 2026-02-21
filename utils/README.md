# Utilities

This directory contains utility functions used throughout the customer support agent.

## Modules

### Validation (`validation.py`)

Validation functions for common data types:

- `validate_email()`: Validate email address format
- `validate_order_id()`: Validate order ID format
- `validate_ticket_id()`: Validate Zendesk ticket ID
- `validate_date()`: Validate date string format
- `validate_required_fields()`: Check for required fields in dictionaries
- `validate_status()`: Validate status against allowed values
- `validate_pagination_params()`: Validate pagination parameters
- `sanitize_string()`: Sanitize string input

**Example:**
```python
from utils.validation import validate_email, validate_order_id

if validate_email("user@example.com"):
    print("Valid email")

if validate_order_id("12345"):
    print("Valid order ID")
```

### Formatting (`formatting.py`)

Formatting functions for displaying data:

- `format_ticket_summary()`: Format Zendesk ticket for display
- `format_order_summary()`: Format order information for display
- `format_datetime()`: Format datetime strings
- `format_date()`: Format date strings
- `format_currency()`: Format currency amounts
- `format_list()`: Format lists as strings
- `format_json()`: Format data as JSON
- `truncate_text()`: Truncate text to maximum length
- `format_error_message()`: Format error messages for users
- `format_tool_result()`: Format tool execution results

**Example:**
```python
from utils.formatting import format_ticket_summary, format_currency

summary = format_ticket_summary(ticket_data)
price = format_currency(99.99)  # "$99.99"
```

### Error Handling (`error_handler.py`)

Error handling utilities and custom exceptions:

**Exceptions:**
- `SupportAgentError`: Base exception
- `IntegrationError`: Integration-related errors
- `ValidationError`: Validation errors
- `ConfigurationError`: Configuration errors

**Functions:**
- `handle_integration_error()`: Handle and format integration errors
- `handle_validation_error()`: Handle validation errors
- `retry_on_failure()`: Decorator for retrying failed operations
- `safe_execute()`: Safely execute functions with error handling

**Example:**
```python
from utils.error_handler import retry_on_failure, IntegrationError

@retry_on_failure(max_retries=3, delay=1.0)
async def fetch_data():
    # Your code here
    pass
```

### Logging (`logger.py`)

Logging utilities:

- `setup_logger()`: Configure logger with file and console handlers
- `get_logger()`: Get logger instance
- `LoggerMixin`: Mixin class to add logging to any class

**Example:**
```python
from utils.logger import setup_logger

logger = setup_logger("my_module", level=logging.INFO, log_file="logs/app.log")
logger.info("Application started")
```

**Using LoggerMixin:**
```python
from utils.logger import LoggerMixin

class MyClass(LoggerMixin):
    def my_method(self):
        self.logger.info("Method called")
```

### Helpers (`helpers.py`)

General helper functions:

- `get_env_var()`: Get environment variable with validation
- `ensure_directory()`: Create directory if it doesn't exist
- `merge_dicts()`: Merge multiple dictionaries
- `filter_dict()`: Filter dictionary by keys
- `exclude_dict_keys()`: Exclude keys from dictionary
- `deep_get()`: Get nested dictionary values using dot notation
- `chunk_list()`: Split list into chunks
- `sanitize_filename()`: Sanitize filenames

**Example:**
```python
from utils.helpers import get_env_var, deep_get, merge_dicts

api_key = get_env_var("API_KEY", required=True)
name = deep_get(user_data, "profile.name", default="Unknown")
merged = merge_dicts(dict1, dict2, dict3)
```

## Usage

Import utilities directly:

```python
from utils import validate_email, format_ticket_summary, setup_logger
```

Or import from specific modules:

```python
from utils.validation import validate_email
from utils.formatting import format_ticket_summary
from utils.error_handler import retry_on_failure
```

## Best Practices

1. **Validation**: Always validate user input before processing
2. **Error Handling**: Use custom exceptions for better error tracking
3. **Logging**: Use structured logging for debugging and monitoring
4. **Formatting**: Use formatting utilities for consistent user-facing output
5. **Helpers**: Use helper functions to reduce code duplication

