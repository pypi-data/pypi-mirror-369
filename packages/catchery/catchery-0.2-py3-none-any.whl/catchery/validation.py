"""
This module contains support functions for validating data.
"""

from typing import Any, Callable, Dict, Union

from .error_handler import ERROR_HANDLER, ErrorSeverity, log_warning

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_object(
    value: Any,
    name: str,
    context: Dict[str, Any] | None = None,
    attributes: list[str] | None = None,
) -> Any:
    """
    Validates that an object exists and optionally has required
    attributes/methods.

    This function checks if the provided `obj` is not `None`. If `attributes` is
    provided, it further checks if the object possesses all specified
    attributes. If any validation fails, an error is logged, and a `ValueError`
    is raised.

    Args:
        obj: The object to validate. name: The human-readable name for the
        object, used in error messages. context: An optional dictionary of
        additional context for logging. attributes: An optional list of strings,
        where each string is the name of an attribute or method that `obj` must
        possess.

    Returns:
        The validated object if all checks pass.

    Raises:
        ValueError: If the object is `None` or is missing any of the
        `attributes`.
    """
    if value is None:
        ERROR_HANDLER.handle(
            error=f"Required value '{name}' is None",
            severity=ErrorSeverity.HIGH,
            context=context or {},
            exception=Exception(f"Required value '{name}' is None"),
            raise_exception=True,
        )
    # If we have attributes to check, validate them.
    if attributes:
        # Gather missing attributes.
        missing_attrs: list[str] = []
        for attribute in attributes:
            if not hasattr(value, attribute):
                missing_attrs.append(attribute)
        # If any attributes are missing, log an error.
        if missing_attrs:
            ERROR_HANDLER.handle(
                error=f"{name} missing required attributes: {missing_attrs}",
                severity=ErrorSeverity.HIGH,
                context={
                    **(context or {}),
                    "object_name": name,
                    "missing_attributes": missing_attrs,
                    "object_type": type(value).__name__,
                },
                exception=Exception(
                    f"{name} missing required attributes: {missing_attrs}"
                ),
                raise_exception=True,
            )
    # If we reach here, the object is valid.
    return value


def validate_type(
    value: Any,
    name: str,
    expected_type: type,
    context: dict[str, Any] | None = None,
) -> Any:
    """
    Validates that a value is of the specified type.

    If the validation fails, an error is logged and a ValueError is raised.

    Args:
        value: The value to validate. expected_type: The expected type (e.g.,
        str, int, list, etc.). name: The name of the parameter being validated,
        used in error messages. context: An optional dictionary of additional
        context for logging.

    Returns:
        The validated value if it is of the expected type.

    Raises:
        ValueError: If the value is not of the expected type.
    """
    # First, validate that the value is not None.
    validate_object(value, name, context)
    # Then, check the type.
    if not isinstance(value, expected_type):
        ERROR_HANDLER.handle(
            error=f"{name} must be of type {expected_type.__name__}, "
            f"got: {type(value).__name__}",
            severity=ErrorSeverity.HIGH,
            context={
                **(context or {}),
                "name": name,
                "expected_type": expected_type.__name__,
                "actual_type": type(value).__name__,
                "value": value,
            },
            exception=ValueError(
                f"Invalid {name}: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            ),
            raise_exception=True,
        )
    return value


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================


def ensure_value(
    value: Any,
    name: str,
    expected_type: Union[Any, tuple[Any, ...]],
    default: Any | None = None,
    context: Dict[str, Any] | None = None,
    allow_none: bool = False,
    validator: Callable[[Any], bool] | None = None,
    converter: Callable[[Any], Any] | None = None,
) -> Any | None:
    """
    Ensures a value is of the specified type, converting or using a default if
    necessary.

    This function attempts to validate and/or convert the provided `value` to
    `expected_type`. If `value` is None and `allow_none` is False, it returns
    `default`. If `value` is not of `expected_type` and a `converter` is
    provided, it attempts conversion. If conversion fails or `value` is still
    not of `expected_type`, it returns `default`. If a `validator` is provided,
    the value (or converted value) must pass the validation. Warnings are logged
    for invalid values or failed conversions.

    Args:
        value: The value to be ensured. name: The human-readable name for the
        value, used in log messages. expected_type: The expected type(s) (e.g.,
        str, int, (int, float)). default: The default value to return if `value`
        is invalid or cannot be converted. context: An optional dictionary of
        additional context for logging. allow_none: If True, `None` is
        considered a valid value if it matches `expected_type`
                    or if `None` is explicitly in `expected_type`. If False,
                    `None` is treated as an invalid value unless `default` is
                    `None`.
        validator: An optional callable that takes the value and returns True if
        valid, False otherwise. converter: An optional callable that takes the
        value and attempts to convert it to `expected_type`.

    Returns:
        The validated and/or converted value, or the `default` value.
    """
    # Get the type name.
    type_name = (
        expected_type.__name__ if isinstance(expected_type, type) else expected_type
    )
    # Make sure the context is valid.
    ctx: dict[str, Any] = {
        **(context or {}),
        "name": name,
        "value": value,
        "actual": type(value).__name__,
        "expected": type_name,
    }
    # Store the value.
    processed_value = value

    # Handle None value.
    if value is None:
        if allow_none and (
            (isinstance(expected_type, tuple) and None in expected_type)
            or expected_type is type(None)
        ):
            return None
        log_warning(
            f"'{name}' is None and not allowed for expected type(s) "
            f"{expected_type}. Using default.",
            ctx,
        )
        return default

    # Attempt conversion if a converter is provided or for common types.
    if not isinstance(processed_value, expected_type):
        log_warning(
            f"'{name}' is not of expected type(s) {type_name}. Attempting conversion.",
            ctx,
        )
        if converter:
            try:
                processed_value = converter(value)
                if not isinstance(processed_value, expected_type):
                    log_warning(
                        f"Converter for '{name}' returned wrong type. "
                        f"Expected {type_name}, "
                        f"got {type(processed_value).__name__}. "
                        f"Using default.",
                        ctx,
                    )
                    return default
            except Exception as e:
                log_warning(
                    f"Conversion of '{name}' failed: {e}. Using default.",
                    {
                        **ctx,
                        "error": str(e),
                    },
                )
                return default
        elif isinstance(expected_type, tuple):
            # Try converting to one of the types in the tuple
            converted_successfully = False
            for t in expected_type:
                try:
                    if t is str and not isinstance(value, str):
                        processed_value = str(value)
                        converted_successfully = True
                        break
                    elif t is int and not isinstance(value, int):
                        processed_value = int(value)
                        converted_successfully = True
                        break
                    elif t is float and not isinstance(value, float):
                        processed_value = float(value)
                        converted_successfully = True
                        break
                except (ValueError, TypeError):
                    continue  # Try next type in tuple

            if not converted_successfully:
                log_warning(
                    f"No converter provided and cannot perform default conversion "
                    f"for '{name}'. Using default.",
                    ctx,
                )
                return default
        else:  # For single expected_type
            if expected_type is str and not isinstance(value, str):
                try:
                    processed_value = str(value)
                except Exception as e:
                    log_warning(
                        f"Default string conversion of '{name}' failed: {e}. "
                        f"Using default.",
                        {
                            **ctx,
                            "error": str(e),
                        },
                    )
                    return default
            elif expected_type is int and not isinstance(value, int):
                try:
                    processed_value = int(value)
                except Exception as e:
                    log_warning(
                        f"Default integer conversion of '{name}' failed: {e}. "
                        f"Using default.",
                        {
                            **ctx,
                            "error": str(e),
                        },
                    )
                    return default
            elif expected_type is float and not isinstance(value, float):
                try:
                    processed_value = float(value)
                except Exception as e:
                    log_warning(
                        f"Default float conversion of '{name}' failed: {e}. "
                        f"Using default.",
                        {
                            **ctx,
                            "error": str(e),
                        },
                    )
                    return default
            else:
                log_warning(
                    f"No converter provided and cannot perform default conversion "
                    f"for '{name}'. Using default.",
                    ctx,
                )
                return default

    # Apply validator if provided
    if validator:
        try:
            if not validator(processed_value):
                log_warning(f"'{name}' failed validation. Using default.", ctx)
                return default
        except Exception as e:
            log_warning(
                f"Validator for '{name}' raised an exception: {e}. Using default.",
                {
                    **ctx,
                    "error": str(e),
                },
            )
            return default

    return processed_value


def ensure_string(
    value: Any,
    name: str,
    default: str = "",
    context: dict[str, Any] | None = None,
) -> str:
    """
    Ensures a value is a string, converting it if possible or using a default.

    This function attempts to convert the provided `value` to a string. If the
    `value` is not already a string, a warning is logged. If conversion is not
    possible (e.g., `value` is `None` and no default is provided), the specified
    `default` string is returned.

    Args:
        value: The value to be ensured as a string. name: The name of the
        parameter being processed, used in log messages. default: The default
        string value to return if `value` cannot be converted or is `None`.
        Defaults to an empty string. context: An optional dictionary of
        additional context for logging.

    Returns:
        The `value` as a string, or the `default` string if conversion fails.
    """
    if not isinstance(value, str):
        log_warning(
            f"{name} should be string, got: {type(value).__name__}, converting",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "type": type(value).__name__,
            },
        )
        return str(value) if value is not None else default
    return value


def ensure_non_negative_int(
    value: Any,
    name: str,
    default: int = 0,
    context: dict[str, Any] | None = None,
) -> int:
    """
    Ensures a value is a non-negative integer, correcting it if necessary.

    This function attempts to convert the provided `value` to an integer and
    ensures it is not negative. If the `value` is not an integer, is negative,
    or cannot be converted, a warning is logged, and the specified `default`
    value is returned or the value is clamped to 0 if it's a negative number.

    Args:
        value: The value to be ensured as a non-negative integer. name: The name
        of the parameter being processed, used in log messages. default: The
        default integer value to return if `value` is invalid. Defaults to 0.
        context: An optional dictionary of additional context for logging.

    Returns:
        The corrected non-negative integer value.
    """
    if not isinstance(value, int) or value < 0:
        log_warning(
            f"{name} must be non-negative integer, got: {value}, "
            f"correcting to {default}",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "corrected_to": default,
            },
        )
        return max(0, int(value) if isinstance(value, (int, float)) else default)
    return value


def ensure_int_in_range(
    value: Any,
    name: str,
    min_val: int,
    max_val: int | None = None,
    default: int | None = None,
    context: dict[str, Any] | None = None,
) -> int:
    """
    Ensures a value is an integer within a specified range, correcting it if
    necessary.

    This function attempts to convert the provided `value` to an integer and
    checks if it falls within the `min_val` and `max_val` (inclusive). If the
    `value` is not an integer, is outside the range, or cannot be converted, a
    warning is logged, and the value is corrected to `min_val`, `max_val`, or
    the specified `default`.

    Args:
        value: The value to be ensured as an integer within the range. name: The
        name of the parameter being processed, used in log messages. min_val:
        The minimum allowed integer value (inclusive). max_val: The maximum
        allowed integer value (inclusive). If `None`, there is no upper limit.
        default: The default integer value to return if `value` is invalid or
        out of range. If `None`, `min_val` is used as the default. context: An
        optional dictionary of additional context for logging.

    Returns:
        The corrected integer value within the specified range.
    """
    if default is None:
        default = min_val

    if (
        not isinstance(value, int)
        or value < min_val
        or (max_val is not None and value > max_val)
    ):
        range_desc = (
            f">= {min_val}" if max_val is None else f"between {min_val} and {max_val}"
        )
        log_warning(
            f"{name} must be integer {range_desc}, got: {value}, "
            f"correcting to {default}",
            {
                **(context or {}),
                "name": name,
                "value": value,
                "min_val": min_val,
                "max_val": max_val,
                "corrected_to": default,
            },
        )

        # Try to convert and clamp
        try:
            converted = int(value) if isinstance(value, (int, float)) else default
            if converted < min_val:
                return min_val
            elif max_val is not None and converted > max_val:
                return max_val
            else:
                return converted
        except (ValueError, TypeError):
            return default
    return value


# Use a helper function for safe type conversion
def _safe_convert(value: Any, target_type: type) -> Any:
    try:
        if target_type is str:
            return str(value) if value is not None else ""
        elif target_type is int:
            return int(value)
        elif target_type is float:
            return float(value)
        else:
            return None
    except (ValueError, TypeError):
        return None


def ensure_list_of_type(
    values: list[Any] | None,
    name: str,
    expected_type: type,
    default: list[Any] | None = None,
    converter: Callable[[Any], Any] | None = None,
    validator: Callable[[Any], bool] | None = None,
    context: dict[str, Any] | None = None,
) -> list[Any]:
    """
    Ensures values is a list containing items of a specified type, correcting if
    needed.

    This function validates that `values` is a list. It then iterates through
    the list to ensure each item is of `expected_type`. Invalid items are either
    converted using a `converter` function, or a default conversion is attempted
    for common types (str, int, float). Items can also be validated with a
    `validator` function. Warnings are logged for invalid items, but execution
    continues with a cleaned list.

    Args:
        values: The list of values to validate, expected to be a list.
        expected_type: The `type` that all items in the list should conform to.
        name: The name of the parameter being processed, used in log messages.
        default: The default list to return if `values` is `None` or not a list.
        Defaults to an empty list. converter: An optional callable that takes an
        item and attempts to convert it to `expected_type`. If conversion fails
        or returns a wrong type, the item is skipped. validator: An optional
        callable that takes an item of `expected_type` and returns returns
        `True` if the item is valid, `False` otherwise. Invalid items are
        skipped. context: An optional dictionary of additional context for
        logging.

    Returns:
        A new list containing only the valid and/or converted items of
        `expected_type`.
    """
    if default is None:
        default = []

    if values is None:
        return default

    if not isinstance(values, list):
        log_warning(
            f"{name} should be list, got: {type(values).__name__}, using default",
            {
                **(context or {}),
                "name": name,
                "value": values,
                "type": type(values).__name__,
            },
        )
        return default

    # Ensure all items are of the expected type
    cleaned_list: list[Any] = []
    had_invalid_items = False

    for i, item in enumerate(values):
        if isinstance(item, expected_type):
            # Item is correct type, now validate if validator is provided
            if validator and not validator(item):
                had_invalid_items = True
                log_warning(
                    f"{name}[{i}] failed validation, " f"skipping item: {item}",
                    {
                        **(context or {}),
                        "name": name,
                        "index": i,
                        "item": item,
                        "expected_type": expected_type.__name__,
                    },
                )
                continue  # Skip invalid items
            else:
                cleaned_list.append(item)
        else:
            # Item is wrong type, try to convert
            had_invalid_items = True
            if converter:
                try:
                    converted_item = converter(item)
                    if isinstance(converted_item, expected_type):
                        # Validate converted item if validator is provided
                        if validator and not validator(converted_item):
                            log_warning(
                                f"{name}[{i}] converted item failed validation, "
                                f"skipping: {converted_item}",
                                {
                                    **(context or {}),
                                    "name": name,
                                    "index": i,
                                    "original": item,
                                    "converted": converted_item,
                                    "expected_type": expected_type.__name__,
                                },
                            )
                            continue
                        cleaned_list.append(converted_item)
                    else:
                        log_warning(
                            f"{name}[{i}] converter returned wrong type, "
                            f"skipping: {item}",
                            {
                                **(context or {}),
                                "name": name,
                                "index": i,
                                "item": item,
                                "expected_type": expected_type.__name__,
                                "converter_result_type": type(converted_item).__name__,
                            },
                        )
                except Exception as e:
                    log_warning(
                        f"{name}[{i}] conversion failed, skipping item: {item}",
                        {
                            **(context or {}),
                            "name": name,
                            "index": i,
                            "item": item,
                            "error": str(e),
                        },
                    )
            else:
                # No converter provided, use default conversion for common types
                try:
                    # Attempt to safely convert the item to the expected type.
                    converted: Any = _safe_convert(item, expected_type)

                    # We failed to do a safe conversion.
                    if converted is None:
                        log_warning(
                            f"{name}[{i}] wrong type and no converter provided, "
                            f"skipping: {item}",
                            {
                                **(context or {}),
                                "name": name,
                                "index": i,
                                "item": item,
                                "expected_type": expected_type.__name__,
                                "actual_type": type(item).__name__,
                            },
                        )
                        continue

                    # Validate converted item if validator is provided.
                    if validator and not validator(converted):
                        log_warning(
                            f"{name}[{i}] converted item failed validation, "
                            f"skipping: {converted}",
                            {
                                **(context or {}),
                                "name": name,
                                "index": i,
                                "original": item,
                                "converted": converted,
                            },
                        )
                        continue

                    cleaned_list.append(converted)
                except (ValueError, TypeError) as e:
                    log_warning(
                        f"{name}[{i}] conversion failed, skipping item: {item}",
                        {
                            **(context or {}),
                            "name": name,
                            "index": i,
                            "item": item,
                            "error": str(e),
                        },
                    )

    if had_invalid_items:
        log_warning(
            f"{name} had invalid items, cleaned list created",
            {
                **(context or {}),
                "name": name,
                "original_length": len(values),
                "cleaned_length": len(cleaned_list),
                "expected_type": expected_type.__name__,
            },
        )

    return cleaned_list


def safe_get_attribute(obj: Any, name: str, default: Any = None) -> Any:
    """
    Safely retrieves an attribute from an object, returning a default value if
    not found.

    This function attempts to get the attribute named `name` from `obj`. If
    `obj` is `None` or the attribute does not exist, a warning is logged, and
    the specified `default` value is returned instead.

    Args:
        obj: The object from which to retrieve the attribute. name: The name of
        the attribute to retrieve. default: The default value to return if the
        attribute is not found or `obj` is `None`. Defaults to `None`.

    Returns:
        The value of the attribute if found, otherwise the `default` value.
    """
    if obj is None:
        return default

    if hasattr(obj, name):
        return getattr(obj, name)
    else:
        log_warning(
            f"{type(obj).__name__} missing attribute '{name}', "
            f"using default: {default}",
            {
                "object_type": type(obj).__name__,
                "name": name,
                "default": default,
            },
        )
        return default
