import pytest
from unittest.mock import patch
from catchery.validation import ensure_value
from catchery.error_handler import (
    log_warning,
)  # Assuming log_warning is directly importable or mocked


# Mock log_warning to capture warnings without affecting actual logging
@pytest.fixture(autouse=True)
def mock_log_warning():
    with patch("catchery.validation.log_warning") as mock:
        yield mock


# --- Basic Functionality Tests ---


def test_ensure_value_correct_type_no_default():
    assert ensure_value(10, "test_int", int) == 10


def test_ensure_value_correct_type_with_default():
    assert ensure_value("hello", "test_str", str, default="world") == "hello"


def test_ensure_value_none_value_allow_none_true():
    assert ensure_value(None, "test_none", str, allow_none=True) is None


def test_ensure_value_none_value_allow_none_false_with_default(mock_log_warning):
    result = ensure_value(
        None, "test_none", str, default="default_str", allow_none=False
    )
    assert result == "default_str"
    mock_log_warning.assert_called_once()
    assert "'test_none' is None and not allowed for expected type(s) <class 'str'>. Using default." in mock_log_warning.call_args[0][0]


def test_ensure_value_none_value_allow_none_false_no_default(mock_log_warning):
    result = ensure_value(None, "test_none", str, allow_none=False)
    assert result is None  # Default is None if not provided
    mock_log_warning.assert_called_once()
    assert "'test_none' is None and not allowed for expected type(s) <class 'str'>. Using default." in mock_log_warning.call_args[0][0]


# --- Type Conversion Tests (Default Converters) ---


def test_ensure_value_convert_str_to_int(mock_log_warning):
    assert ensure_value("123", "test_int_conversion", int) == 123
    mock_log_warning.assert_called_once()
    assert (
        "is not of expected type(s) int. Attempting conversion."
        in mock_log_warning.call_args[0][0]
    )


def test_ensure_value_convert_float_to_int(mock_log_warning):
    assert ensure_value(123.45, "test_int_conversion", int) == 123
    mock_log_warning.assert_called_once()
    assert (
        "is not of expected type(s) int. Attempting conversion."
        in mock_log_warning.call_args[0][0]
    )


def test_ensure_value_convert_int_to_str(mock_log_warning):
    assert ensure_value(123, "test_str_conversion", str) == "123"
    mock_log_warning.assert_called_once()
    assert (
        "is not of expected type(s) str. Attempting conversion."
        in mock_log_warning.call_args[0][0]
    )


def test_ensure_value_convert_str_to_float(mock_log_warning):
    assert ensure_value("123.45", "test_float_conversion", float) == 123.45
    mock_log_warning.assert_called_once()
    assert (
        "is not of expected type(s) float. Attempting conversion."
        in mock_log_warning.call_args[0][0]
    )


def test_ensure_value_failed_default_conversion_with_default(mock_log_warning):
    result = ensure_value("abc", "test_failed_int_conversion", int, default=0)
    assert result == 0
    assert (
        mock_log_warning.call_count == 2
    )  # One for type mismatch, one for conversion failure


def test_ensure_value_failed_default_conversion_no_default(mock_log_warning):
    result = ensure_value("abc", "test_failed_int_conversion", int)
    assert result is None
    assert (
        mock_log_warning.call_count == 2
    )  # One for type mismatch, one for conversion failure


# --- Custom Converter Tests ---


def test_ensure_value_custom_converter_success():
    def custom_converter(val):
        return int(val * 2)

    assert (
        ensure_value(5.0, "test_custom_converter", int, converter=custom_converter)
        == 10
    )


def test_ensure_value_custom_converter_failure_with_default(mock_log_warning):
    def custom_converter_failing(val):
        raise ValueError("Conversion error")

    result = ensure_value(
        "invalid",
        "test_custom_converter_fail",
        int,
        default=99,
        converter=custom_converter_failing,
    )
    assert result == 99
    assert (
        mock_log_warning.call_count == 2
    )  # One for type mismatch, one for conversion failure


# --- Validator Tests ---


def test_ensure_value_validator_success():
    def is_positive(val):
        return val > 0

    assert ensure_value(10, "test_validator", int, validator=is_positive) == 10


def test_ensure_value_validator_failure_with_default(mock_log_warning):
    def is_positive(val):
        return val > 0

    result = ensure_value(
        -5, "test_validator_fail", int, default=1, validator=is_positive
    )
    assert result == 1
    mock_log_warning.assert_called_once()
    assert "failed validation" in mock_log_warning.call_args[0][0]


def test_ensure_value_validator_raises_exception_with_default(mock_log_warning):
    def validator_raises(val):
        if val == 10:
            raise ValueError("Validation exception")
        return True

    result = ensure_value(
        10, "test_validator_exception", int, default=0, validator=validator_raises
    )
    assert result == 0
    mock_log_warning.assert_called_once()
    assert (
        "Validator for 'test_validator_exception' raised an exception"
        in mock_log_warning.call_args[0][0]
    )


# --- Combined Scenarios ---


def test_ensure_value_conversion_and_validation_success(mock_log_warning):
    def is_even(val):
        return val % 2 == 0

    assert ensure_value("20", "test_conv_val_success", int, validator=is_even) == 20
    mock_log_warning.assert_called_once()  # Only for initial type mismatch


def test_ensure_value_conversion_success_validation_failure(mock_log_warning):
    def is_even(val):
        return val % 2 == 0

    result = ensure_value("21", "test_conv_val_fail", int, default=0, validator=is_even)
    assert result == 0
    assert (
        mock_log_warning.call_count == 2
    )  # One for type mismatch, one for validation failure


# --- Multiple Expected Types ---


def test_ensure_value_multiple_expected_types_success():
    assert ensure_value(10, "test_multi_type_int", (int, float)) == 10
    assert ensure_value(10.5, "test_multi_type_float", (int, float)) == 10.5


def test_ensure_value_multiple_expected_types_conversion(mock_log_warning):
    assert ensure_value("10", "test_multi_type_str_to_int", (int, float)) == 10
    mock_log_warning.assert_called_once()


def test_ensure_value_multiple_expected_types_none_not_allowed(mock_log_warning):
    result = ensure_value(
        None, "test_multi_type_none_not_allowed", (int, float), default=0
    )
    assert result == 0
    mock_log_warning.assert_called_once()


def test_ensure_value_multiple_expected_types_none_allowed():
    assert (
        ensure_value(
            None, "test_multi_type_none_allowed", (int, type(None)), allow_none=True
        )
        is None
    )


def test_ensure_value_none_value_allow_none_true_but_not_expected_type(
    mock_log_warning,
):
    result = ensure_value(None, "test_none", int, default=100, allow_none=True)
    assert result == 100
    mock_log_warning.assert_called_once()
    assert (
        "'test_none' is None and not allowed for expected type(s) <class 'int'>. Using default."
        in mock_log_warning.call_args[0][0]
    )


# --- Edge Cases and Specific Scenarios ---


def test_ensure_value_no_default_and_failure(mock_log_warning):
    result = ensure_value("abc", "test_no_default", int)
    assert result is None
    assert mock_log_warning.call_count == 2


def test_ensure_value_empty_string_to_int_with_default(mock_log_warning):
    result = ensure_value("", "test_empty_str_to_int", int, default=0)
    assert result == 0
    assert mock_log_warning.call_count == 2


def test_ensure_value_boolean_to_int(mock_log_warning):
    assert ensure_value(True, "test_bool_to_int", int) == 1


def test_ensure_value_boolean_to_str(mock_log_warning):
    assert ensure_value(False, "test_bool_to_str", str) == "False"
    mock_log_warning.assert_called_once()


def test_ensure_value_object_to_str(mock_log_warning):
    class MyClass:
        def __str__(self):
            return "MyClassInstance"

    obj = MyClass()
    assert ensure_value(obj, "test_obj_to_str", str) == "MyClassInstance"
    mock_log_warning.assert_called_once()


def test_ensure_value_context_passed_to_log_warning(mock_log_warning):
    test_context = {"source": "my_module", "id": 123}
    ensure_value("abc", "test_context", int, default=0, context=test_context)
    assert mock_log_warning.call_count == 2
    # Check if context is part of the logged warning's context dictionary
    logged_context = mock_log_warning.call_args[0][1]
    assert logged_context["source"] == "my_module"
    assert logged_context["id"] == 123
    assert "name" in logged_context
    assert "value" in logged_context


def test_ensure_value_no_converter_no_default_conversion_possible(mock_log_warning):
    class CustomObject:
        pass

    obj = CustomObject()
    result = ensure_value(obj, "test_no_conv_possible", int, default=0)
    assert result == 0
    assert (
        mock_log_warning.call_count == 2
    )  # One for type mismatch, one for no converter/default conversion


def test_ensure_value_no_converter_no_default_conversion_possible_no_default(
    mock_log_warning,
):
    class CustomObject:
        pass

    obj = CustomObject()
    result = ensure_value(obj, "test_no_conv_possible_no_default", int)
    assert result is None
    assert mock_log_warning.call_count == 2
