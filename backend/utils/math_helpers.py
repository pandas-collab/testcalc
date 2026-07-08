import sys
from decimal import Decimal

# Define safe numeric limits
MAX_SAFE_INTEGER = sys.maxsize
MIN_SAFE_INTEGER = -sys.maxsize - 1
MAX_SAFE_FLOAT = sys.float_info.max / 2  # Use half to prevent overflow in operations
MIN_SAFE_FLOAT = -sys.float_info.max / 2

def safe_divide(dividend, divisor):
    """
    Perform safe division with zero-check

    Args:
        dividend: Number to be divided
        divisor: Number to divide by

    Returns:
        Division result as Decimal

    Raises:
        ZeroDivisionError: If divisor is zero
    """
    if divisor == 0:
        raise ZeroDivisionError("Division by zero")

    # Convert to Decimal for precision
    if not isinstance(dividend, Decimal):
        dividend = Decimal(str(dividend))
    if not isinstance(divisor, Decimal):
        divisor = Decimal(str(divisor))

    result = dividend / divisor
    return result

def check_overflow(number):
    """
    Check if number exceeds safe limits

    Args:
        number: Number to check

    Raises:
        OverflowError: If number exceeds safe limits
        ValueError: If number is not finite
    """
    if not isinstance(number, (int, float, Decimal)):
        raise ValueError("Input must be a number")

    # Convert to float for checking
    if isinstance(number, Decimal):
        try:
            num_float = float(number)
        except (ValueError, OverflowError):
            raise OverflowError("Number too large to represent")
    else:
        num_float = float(number)

    # Check for infinity and NaN
    if not is_finite(num_float):
        raise ValueError("Number must be finite")

    # Check overflow limits
    if isinstance(number, int):
        if number > MAX_SAFE_INTEGER or number < MIN_SAFE_INTEGER:
            raise OverflowError("Integer exceeds safe limits")
    else:
        if abs(num_float) > MAX_SAFE_FLOAT:
            raise OverflowError("Number exceeds safe limits")

def is_finite(number):
    """
    Check if number is finite (not infinity or NaN)

    Args:
        number: Number to check

    Returns:
        bool: True if number is finite
    """
    try:
        import math
        return math.isfinite(number)
    except (TypeError, ValueError):
        return False

def clamp(value, min_val, max_val):
    """
    Clamp value between minimum and maximum bounds

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))

def round_to_precision(number, precision=10):
    """
    Round number to specified decimal precision

    Args:
        number: Number to round
        precision: Decimal places (default 10)

    Returns:
        Rounded number
    """
    if not isinstance(precision, int) or precision < 0 or precision > 15:
        precision = 10

    return round(float(number), precision)
