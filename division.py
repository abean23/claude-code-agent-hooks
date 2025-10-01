def divide(a, b):
    """
    Divides two numbers and returns the result.

    Args:
        a: The numerator (dividend)
        b: The denominator (divisor)

    Returns:
        The result of a divided by b

    Raises:
        ZeroDivisionError: If b is zero
        TypeError: If inputs are not numeric
        ValueError: If inputs are invalid
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numeric")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
