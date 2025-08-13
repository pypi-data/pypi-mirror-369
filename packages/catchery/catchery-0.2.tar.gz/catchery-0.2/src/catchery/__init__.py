"""
Catchery is a Python library for building robust and scalable applications.
"""

from .error_handler import (
    AppError,
    ErrorHandler,
    ErrorSeverity,
    log_critical,
    log_error,
    log_info,
    log_warning,
    safe_operation,
)
from .validation import (
    ensure_int_in_range,
    ensure_list_of_type,
    ensure_non_negative_int,
    ensure_string,
    safe_get_attribute,
    validate_object,
    validate_type,
)

__all__ = [
    "AppError",
    "ErrorHandler",
    "ErrorSeverity",
    "safe_operation",
    "log_info",
    "log_warning",
    "log_error",
    "log_critical",
    # Validation functions.
    "validate_object",
    "validate_type",
    "ensure_string",
    "ensure_non_negative_int",
    "ensure_int_in_range",
    "ensure_list_of_type",
    "safe_get_attribute",
]
