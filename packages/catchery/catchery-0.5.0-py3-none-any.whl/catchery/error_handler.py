"""
Centralized error handling and logging system.
"""

# =============================================================================
# Imports & Type Aliases
# =============================================================================

import json
import logging
import threading
from collections import deque
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Deque, Dict, List, Protocol, Type, TypeVar

T = TypeVar("T")


# =============================================================================
# Core Enums & Data Classes
# =============================================================================


class ErrorSeverity(Enum):
    """
    Enumeration of error severity levels for the error handling system.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AppError:
    """
    Represents an application error with severity, context, and optional
    exception information.
    """

    message: str
    severity: ErrorSeverity
    context: dict[str, Any]
    exception: Exception | None = None


class ErrorCallback(Protocol):
    def __call__(self, error: AppError) -> None: ...


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for logging records."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            A JSON string representation of the log record.
        """
        log_record: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
        # Add any extra attributes passed to the log record
        for key, value in record.__dict__.items():
            if key not in log_record and not key.startswith("_"):
                log_record[key] = value
        # Ensure all values in log_record are JSON serializable
        serializable_log_record = self._safe_json_serialize(log_record)
        return json.dumps(serializable_log_record)

    def _safe_json_serialize(self, obj: Any) -> Any:
        """
        Recursively converts non-JSON-serializable objects within a structure
        to their string representation.
        """
        if isinstance(obj, dict):
            return {k: self._safe_json_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._safe_json_serialize(elem) for elem in obj]
        try:
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            return repr(obj)


class ErrorHandler:
    """
    Centralized error handling for the application.

    Features:
        - Thread-safe error history (with max size)
        - Customizable logger
        - Structured logging (JSON)
        - Error callbacks/hooks
        - Exception chaining
        - Context manager for contextual data (thread-local)
        - Testing utilities (capture errors)
    """

    _thread_local = threading.local()

    def _get_thread_context(self) -> dict[str, Any]:
        """
        Retrieves the merged thread-local context from the stack.

        Returns:
            A dictionary containing the merged thread-local context.
        """
        if not hasattr(self._thread_local, "context_stack"):
            self._thread_local.context_stack = []

        merged_context: dict[str, Any] = {}
        for context_dict in self._thread_local.context_stack:
            merged_context.update(context_dict)
        return merged_context

    class Context:
        """
        Context manager for adding contextual data to all errors in this thread.
        Supports nesting.

        Usage:
            with handler.Context(user_id=123):
                handler.handle(...)
        """

        def __init__(self, **context: Any) -> None:
            """
            Initializes the context manager with the given context data.

            Args:
                **context: Arbitrary keyword arguments representing the context
                data.
            """
            self.context = context

        def __enter__(self) -> None:
            """
            Enters the runtime context, pushing the new context onto the stack.
            """
            if not hasattr(ErrorHandler._thread_local, "context_stack"):
                ErrorHandler._thread_local.context_stack = []
            ErrorHandler._thread_local.context_stack.append(self.context)

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            """
            Exits the runtime context, popping the context from the stack.

            Args:
                exc_type: The exception type, if an exception was raised.
                exc_val: The exception value, if an exception was raised.
                exc_tb: The traceback, if an exception was raised.
            """
            if hasattr(ErrorHandler._thread_local, "context_stack"):
                if ErrorHandler._thread_local.context_stack:
                    ErrorHandler._thread_local.context_stack.pop()
                else:
                    # This case should ideally not happen if enter/exit are balanced
                    pass
            else:
                # This case should ideally not happen if enter/exit are balanced
                pass

    class CaptureErrors:
        """
        Context manager to capture errors handled during the block.

        Usage:
            with handler.CaptureErrors(handler) as errors:
                handler.handle(...)
            # errors is a list of AppError
        """

        def __init__(self, handler: "ErrorHandler") -> None:
            """
            Initializes the error capture context manager.

            Args:
                handler: The ErrorHandler instance to capture errors from.
            """
            self.handler: ErrorHandler = handler
            self.captured: List[AppError] = []

        def _callback(self, error: AppError) -> None:
            """
            Callback function to append captured errors to the list.

            Args:
                error: The AppError instance to capture.
            """
            self.captured.append(error)

        def __enter__(self) -> List[AppError]:
            """
            Enters the runtime context, registering the capture callback.

            Returns:
                A list that will contain the captured AppError instances.
            """
            self.handler.register_callback(self._callback)
            return self.captured

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            """
            Exits the runtime context, restoring original callbacks.

            Args:
                exc_type: The exception type, if an exception was raised.
                exc_val: The exception value, if an exception was raised.
                exc_tb: The traceback, if an exception was raised.
            """
            # Remove the capture callback. This assumes it's still in the list.
            # If the list was modified externally, this might not work as expected.
            try:
                self.handler._callbacks.remove(self._callback)
            except ValueError:
                # Callback not found, likely removed or list modified externally
                pass

    def __init__(
        self,
        logger: logging.Logger | None = None,
        error_history_maxlen: int = 1000,
        use_json_logging: bool = False,
        plain_text_formatter: logging.Formatter | None = None,
    ) -> None:
        """
        Initialize the ErrorHandler.

        Args:
            logger: Optional custom logger instance. error_history_maxlen: Max
            number of errors to keep in history. use_json_logging: If True, logs
            in JSON format.
        """
        self.error_history: Deque[AppError] = deque(maxlen=error_history_maxlen)
        self._lock = threading.Lock()
        self._callbacks: List[ErrorCallback] = []
        self._use_json_logging = use_json_logging
        self._stored_handlers: List[logging.Handler] = []
        self._plain_text_formatter = plain_text_formatter or logging.Formatter(
            "[%(asctime)s] %(levelname)-8s: %(message)s", datefmt="%H:%M:%S"
        )

        if logger is None:
            self.logger = logging.getLogger("ErrorHandler")
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
        else:
            self.logger = logger

        if self._use_json_logging:
            self.set_json_logging()
        else:
            self.set_plain_text_logging()

    def get_logger(self) -> logging.Logger:
        """
        Returns the logger instance used by the ErrorHandler.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger

    def set_plain_text_formatter(self, formatter: logging.Formatter) -> None:
        """
        Sets a custom plain text formatter for the logger.

        Args:
            formatter: The logging.Formatter instance to use for plain text
            logging.
        """
        self._plain_text_formatter = formatter
        if not self._use_json_logging:
            self._set_formatter_to_handlers(formatter)

    def set_plain_text_logging(self) -> None:
        """
        Configures the logger to use plain text formatting.
        """
        self._set_formatter_to_handlers(self._plain_text_formatter)
        self._use_json_logging = False

    def set_json_logging(self) -> None:
        """
        Configures the logger to use JSON formatting.
        """
        self._set_formatter_to_handlers(JsonFormatter())
        self._use_json_logging = True

    def _set_formatter_to_handlers(self, formatter: logging.Formatter) -> None:
        """
        Sets the given formatter to all handlers of the logger.

        Args:
            formatter: The logging.Formatter instance to set.
        """
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)

    def register_callback(self, callback: ErrorCallback) -> None:
        """Register a callback to be called on every error."""
        self._callbacks.append(callback)

    def handle(
        self,
        error: AppError | str,
        severity: ErrorSeverity | None = None,
        context: Dict[str, Any] | None = None,
        exception: Exception | None = None,
        raise_exception: bool = False,
        chain_exception: Exception | None = None,
        stack_offset: int = 0,
    ) -> None:
        """
        Handle an error by either receiving an AppErrWor instance or the full
        list of attributes.

        Usage:
            handle(AppError(...)) handle("error", severity, context, exception,
            ...)

        Args:
            error: Either an AppError instance or the error error string.
            severity: The severity level of the error (required if not passing
                      AppError).
            context: An optional dictionary of contextual data. exception: An
            optional exception object associated with the error.
            raise_exception: If True, re-raises the `exception` after handling.
            chain_exception: An optional exception to chain with `exception`.
        """
        if not isinstance(error, AppError):
            if severity is None:
                raise ValueError(
                    "'severity' must be provided when not passing an AppError."
                )
            error = AppError(
                message=error,
                severity=severity,
                context={**self._get_thread_context(), **(context or {})},
                exception=exception,
            )

        # Store the error in history and notify registered callbacks.
        with self._lock:
            self.error_history.append(error)

        for cb in self._callbacks:
            try:
                cb(error)
            except Exception:
                # Prevent a faulty callback from disrupting error handling
                self.logger.exception("Error in error handler callback")

        # Determine the appropriate logging method based on severity.
        log_method = {
            ErrorSeverity.LOW: self.logger.info,
            ErrorSeverity.MEDIUM: self.logger.warning,
            ErrorSeverity.HIGH: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical,
        }.get(error.severity, self.logger.info)

        # Log the error using either JSON or plain text format.
        log_kwargs: Dict[str, Any] = {
            "extra": {f"ctx_{k}": v for k, v in error.context.items()}
        }

        if self._use_json_logging:
            # Add structured data to extra for JSON logging
            log_kwargs["extra"]["severity"] = error.severity.value
            log_kwargs["extra"]["context"] = error.context
            log_kwargs["extra"]["exception"] = (
                str(error.exception) if error.exception else None
            )
            # Log the error with the original message and structured extra data.
            log_method(
                msg=error.message,
                **log_kwargs,
                stacklevel=2 + stack_offset,
            )
        else:
            # Append context to the message for plain text logging
            full_message = error.message
            if error.context:
                # Get the context as a list of key=value strings.
                lst = [f"{k}={v}" for k, v in error.context.items()]
                # Create a context string from the list.
                context_str = ", ".join(lst)
                # Build the full message.
                full_message = f"{error.message} ({context_str})"
            # Log the error.
            log_method(msg=full_message, stacklevel=2 + stack_offset)

        # Raise an exception if requested, with optional chaining.
        if raise_exception and error.exception:
            if chain_exception:
                raise error.exception from chain_exception
            raise error.exception

    def safe_execute(
        self,
        operation: Callable[[], T],
        default: T,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Dict[str, Any] | None = None,
    ) -> T:
        """
        Safely executes an operation, handling any exceptions that occur.

        If an exception is raised during the operation, it is caught, logged,
        and the specified default value is returned. The exception is not
        re-raised unless `raise_exception` is explicitly set to True within the
        `handle` method.

        Args:
            operation: A callable (function or lambda) representing the
            operation
                       to execute. It should take no arguments and return a
                       value of type T.
            default: The default value to return if an exception occurs during
                     the operation.
            error_message: A descriptive message for the error, used in logging.
            severity: The severity level of the error if one occurs (default:
            MEDIUM). context: An optional dictionary of additional context to
            include
                     with the error log.

        Returns:
            The result of the `operation` if successful, or the `default` value
            if an exception occurs.
        """
        try:
            return operation()
        except Exception as e:
            self.handle(
                error=error_message,
                severity=severity,
                context=context,
                exception=e,
                stack_offset=1,
            )
            return default


# Global error handler instance
_default_global_error_handler: ErrorHandler | None = None


def get_default_handler() -> ErrorHandler:
    """
    Returns the default global ErrorHandler instance.
    Initializes it if it hasn't been initialized yet.
    """
    global _default_global_error_handler
    if _default_global_error_handler is None:
        _default_global_error_handler = ErrorHandler()
        # Ensure the default logger has at least one handler if it's newly created
        if not _default_global_error_handler.logger.handlers:
            handler = logging.StreamHandler()
            _default_global_error_handler.logger.addHandler(handler)
    return _default_global_error_handler


def set_default_handler(handler: ErrorHandler | None) -> None:
    """
    Sets the global ErrorHandler instance.
    This is primarily for testing or advanced configuration.
    """
    global _default_global_error_handler
    _default_global_error_handler = handler


# ==============================================================================
# VALIDATION HELPERS
# ==============================================================================


def safe_operation(
    default_value: Any = None,
    error_message: str = "Operation failed",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for safe operation execution.

    Args:
        default_value (Any): Default value to return on error. error_message
        (str): Error message prefix for logging. severity (ErrorSeverity):
        Severity level for errors.

    Returns:
        Callable: The decorator function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper function that executes the decorated function safely."""
            return get_default_handler().safe_execute(
                lambda: func(*args, **kwargs),
                default_value,
                error_message,
                severity,
            )

        return wrapper

    return decorator


def re_raise_chained(
    new_exception_type: Type[Exception],
    message: str,
    severity: ErrorSeverity = ErrorSeverity.HIGH,
    context: Dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator that catches exceptions from the decorated function, logs them,
    and then re-raises a new, specified exception, chaining it to the original.

    Args:
        new_exception_type (Type[Exception]): The type of exception to re-raise.
        message (str): The message for the new exception.
        severity (ErrorSeverity): The severity level for logging the original error.
        context (Dict[str, Any] | None): Additional context for logging.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as original_exception:
                handler = get_default_handler()
                # Log the original exception with its context
                handler.handle(
                    error=f"Error in '{func.__name__}': {original_exception}",
                    severity=severity,
                    context={**(context or {}), "function_name": func.__name__},
                    exception=original_exception,
                    raise_exception=False # Log it, but don't re-raise the original
                )
                # Re-raise the new exception, explicitly chaining it to the original
                raise new_exception_type(message) from original_exception
        return wrapper
    return decorator


# ==============================================================================
# CONVENIENCE LOGGING FUNCTIONS
# ==============================================================================


def log_info(
    message: str,
    context: Dict[str, Any] | None = None,
    exception: Exception | None = None,
    raise_exception: bool = False,
    chain_exception: Exception | None = None,
) -> None:
    """
    Logs an info-level message using the global error handler.

    Args:
        message: The primary message describing the informational event.
        context: An optional dictionary of additional context to include with
        the log. exception: An optional exception object to include with the
        log. raise_exception: If True, re-raises the `exception` after handling.
        chain_exception: An optional exception to chain with `exception`.
    """
    get_default_handler().handle(
        message,
        ErrorSeverity.LOW,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
        stack_offset=1,
    )


def log_warning(
    message: str,
    context: dict[str, Any] | None = None,
    exception: Exception | None = None,
    raise_exception: bool = False,
    chain_exception: Exception | None = None,
) -> None:
    """
    Logs a warning-level message using the global error handler.

    Args:
        message: The primary message describing the warning event. context: An
        optional dictionary of additional context to include with the log.
        exception: An optional exception object to include with the log.
        raise_exception: If True, re-raises the `exception` after handling.
        chain_exception: An optional exception to chain with `exception`.
    """
    get_default_handler().handle(
        message,
        ErrorSeverity.MEDIUM,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
        stack_offset=1,
    )


def log_error(
    message: str,
    context: dict[str, Any] | None = None,
    exception: Exception | None = None,
    raise_exception: bool = False,
    chain_exception: Exception | None = None,
) -> None:
    """
    Logs an error-level message using the global error handler.

    Args:
        message: The primary message describing the error event. context: An
        optional dictionary of additional context to include with the log.
        exception: An optional exception object to include with the log.
        raise_exception: If True, re-raises the `exception` after handling.
        chain_exception: An optional exception to chain with `exception`.
    """
    get_default_handler().handle(
        message,
        ErrorSeverity.HIGH,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
        stack_offset=1,
    )


def log_critical(
    message: str,
    context: dict[str, Any] | None = None,
    exception: Exception | None = None,
    raise_exception: bool = False,
    chain_exception: Exception | None = None,
) -> None:
    """
    Logs a critical-level message using the global error handler.

    Args:
        message: The primary message describing the critical event. context: An
        optional dictionary of additional context to include with the log.
        exception: An optional exception object to include with the log.
        raise_exception: If True, re-raises the `exception` after handling.
        chain_exception: An optional exception to chain with `exception`.
    """
    get_default_handler().handle(
        message,
        ErrorSeverity.CRITICAL,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
        stack_offset=1,
    )
