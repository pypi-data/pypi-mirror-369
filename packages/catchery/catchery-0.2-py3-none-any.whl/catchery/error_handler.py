"""
Centralized error handling and logging system.
"""

# =============================================================================
# Imports & Type Aliases
# =============================================================================

import inspect
import json
import logging
import threading
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Protocol, TypeVar

T = TypeVar("T")


# =============================================================================
# Core Enums & Data Classes
# =============================================================================


def _find_project_root() -> Path:
    """
    Attempts to find the project root by looking for sentinel files/directories.
    Searches upwards from the current file's location.
    """
    current_file_path = Path(__file__).resolve()
    current_dir = current_file_path.parent

    # Define potential sentinel files/directories
    sentinels = [".git", "pyproject.toml", "README.md"]

    for parent in current_dir.parents:
        for sentinel in sentinels:
            if (parent / sentinel).exists():
                return parent
    # Fallback if no sentinel is found
    return Path.cwd()


def _get_caller_info(skip_frames: int = 2) -> tuple[str, int]:
    """
    Get the file path and line number of the caller.

    Args:
        skip_frames: Number of frames to skip (default 2: this function +
                     the logging function)

    Returns:
        tuple: (relative_file_path, line_number)
    """
    try:
        project_root = _find_project_root()
        stack = inspect.stack()

        # Ensure there are enough frames to skip
        if len(stack) <= skip_frames:
            return "unknown", 0

        frame_info = stack[skip_frames]
        file_path = Path(frame_info.filename)
        line_number = frame_info.lineno

        try:
            rel_path = file_path.relative_to(project_root)
            return str(rel_path), line_number
        except ValueError:
            # file_path is not under project_root.
            return file_path.name, line_number
    except Exception:
        return "unknown", 0


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
        return json.dumps(log_record)


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

    class Context:
        """
        Context manager for adding contextual data to all errors in this thread.

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
            Enters the runtime context, setting the thread-local context.
            """
            ErrorHandler._thread_local.context = self.context

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            """
            Exits the runtime context, clearing the thread-local context.

            Args:
                exc_type: The exception type, if an exception was raised.
                exc_val: The exception value, if an exception was raised.
                exc_tb: The traceback, if an exception was raised.
            """
            ErrorHandler._thread_local.context = None

    def _get_thread_context(self) -> dict[str, Any]:
        """
        Retrieves the thread-local context dictionary.

        Returns:
            A dictionary containing the thread-local context.
        """
        context = getattr(self._thread_local, "context", None)
        return context if context is not None else {}

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
            self._orig_callbacks: List[ErrorCallback] | None = None
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
            self._orig_callbacks = list(self.handler._callbacks)
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
            if self._orig_callbacks is not None:
                self.handler._callbacks = self._orig_callbacks
            else:
                self.handler._callbacks = []

    def __init__(
        self,
        logger: logging.Logger | None = None,
        error_history_maxlen: int = 1000,
        use_json_logging: bool = False,
    ) -> None:
        """
        Initialize the ErrorHandler.

        Args:
            logger: Optional custom logger instance. error_history_maxlen: Max
            number of errors to keep in history. use_json_logging: If True, logs
            in JSON format.
        """
        self.logger: logging.Logger = logger or logging.getLogger("app_errors")
        self.error_history: Deque[AppError] = deque(maxlen=error_history_maxlen)
        self._lock = threading.Lock()
        self._callbacks: List[ErrorCallback] = []
        self.use_json_logging = use_json_logging

        # Set up the formatter based on the initial use_json_logging value.
        self.set_json_logging(use_json_logging)

    def set_json_logging(self, enable: bool) -> None:
        """
        Configures the logger to use a custom JSON formatter based on the
        'enable' flag. Removes existing handlers to prevent duplicate logs and
        adds a new StreamHandler.
        """
        # Remove existing handlers to prevent duplicate logs.
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)

        # Create a new handler.
        handler = logging.StreamHandler()

        # Set the formatter based on the 'enable' flag.
        if enable:
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )

        # Add the handler to the logger.
        self.logger.addHandler(handler)
        self.use_json_logging = enable

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
            error = self._create_app_error(error, severity, context, exception)
        self._store_and_notify(error)
        self._log_error(error)
        self._raise_if_needed(error, raise_exception, chain_exception)

    def _create_app_error(
        self,
        message: str,
        severity: ErrorSeverity,
        context: Dict[str, Any] | None,
        exception: Exception | None,
    ) -> AppError:
        """
        Create an AppError object with merged context and caller info.

        Args:
            message: The primary error message. severity: The severity level of
            the error. context: An optional dictionary of contextual data.
            exception: An optional exception object.

        Returns:
            An `AppError` instance fully populated with error details.
        """
        file_path, line_number = _get_caller_info(skip_frames=4)
        merged_context: dict[str, Any] = {
            **self._get_thread_context(),
            **(context or {}),
            "location": f"{file_path}:{line_number}",
        }
        return AppError(
            message=message,
            severity=severity,
            context=merged_context,
            exception=exception,
        )

    def _store_and_notify(self, error: AppError) -> None:
        """
        Store the error in history and notify registered callbacks.

        Args:
            error: The `AppError` object to store and dispatch.
        """
        with self._lock:
            self.error_history.append(error)

        for cb in self._callbacks:
            try:
                cb(error)
            except Exception:
                # Prevent a faulty callback from disrupting error handling
                self.logger.exception("Error in error handler callback")

    def _get_log_method(self, severity: ErrorSeverity) -> Callable[..., None]:
        """
        Determine the appropriate logging method based on severity.

        Args:
            severity: The severity level of the error.

        Returns:
            The corresponding logger method (e.g., `logger.info`,
            `logger.error`).
        """
        return {
            ErrorSeverity.LOW: self.logger.info,
            ErrorSeverity.MEDIUM: self.logger.warning,
            ErrorSeverity.HIGH: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical,
        }.get(severity, self.logger.info)

    def _log_error(self, error: AppError) -> None:
        """
        Log the error using either JSON or plain text format.

        Args:
            error: The `AppError` object to log.
        """
        log_method = self._get_log_method(error.severity)
        log_kwargs: Dict[str, Any] = {
            "extra": {f"ctx_{k}": v for k, v in error.context.items()}
        }
        if error.exception:
            log_kwargs["exc_info"] = error.exception

        if self.use_json_logging:
            log_record: dict[str, Any] = {
                "severity": error.severity.value,
                "message": error.message,
                "context": error.context,
                "exception": str(error.exception) if error.exception else None,
            }
            log_method(json.dumps(log_record), **log_kwargs)
        else:
            location = error.context.get("location", "unknown")
            formatted_message = (
                f"{error.severity.value.upper()}: {location} - {error.message}"
            )
            log_method(formatted_message, **log_kwargs)

    def _raise_if_needed(
        self,
        error: AppError,
        raise_exception: bool,
        chain_exception: Exception | None,
    ) -> None:
        """
        Raise an exception if requested, with optional chaining.

        Args:
            error: The `AppError` containing the exception to potentially raise.
            raise_exception: A boolean indicating whether to raise the
            exception. chain_exception: An optional exception to chain from.

        Raises:
            Exception: The exception from the `error` object if
            `raise_exception`
                       is True.
        """
        if not raise_exception or not error.exception:
            return

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
            )
            return default


# Global error handler instance
ERROR_HANDLER = ErrorHandler(use_json_logging=True)

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
            return ERROR_HANDLER.safe_execute(
                lambda: func(*args, **kwargs),
                default_value,
                error_message,
                severity,
            )

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
    ERROR_HANDLER.handle(
        message,
        ErrorSeverity.LOW,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
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
    ERROR_HANDLER.handle(
        message,
        ErrorSeverity.MEDIUM,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
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
    ERROR_HANDLER.handle(
        message,
        ErrorSeverity.HIGH,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
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
    ERROR_HANDLER.handle(
        message,
        ErrorSeverity.CRITICAL,
        context,
        exception,
        raise_exception=raise_exception,
        chain_exception=chain_exception,
    )
