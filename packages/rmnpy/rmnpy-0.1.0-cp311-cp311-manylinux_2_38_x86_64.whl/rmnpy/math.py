# -*- coding: utf-8 -*-
"""
Mathematical functions for RMNpy Scalar objects.

This module provides mathematical functions that work with physical quantities
represented as Scalar objects, including proper unit handling and dimensional
analysis.

Functions are organized into categories:
- Trigonometric: sin, cos, tan, asin, acos, atan, atan2
- Hyperbolic: sinh, cosh, tanh, asinh, acosh, atanh
- Exponential/Logarithmic: exp, log, log10, log2
- Power: sqrt, cbrt, pow
- Constants: pi, e, tau

All functions automatically handle unit conversions and validate dimensional
compatibility.
"""

import cmath
import math
from typing import Callable, Union

from rmnpy.exceptions import RMNError
from rmnpy.wrappers.sitypes.scalar import Scalar


def _validate_scalar(value: object, function_name: str) -> None:
    """Validate that input is a Scalar object."""
    if not isinstance(value, Scalar):
        raise TypeError(
            f"{function_name}() requires a Scalar object, got {type(value).__name__}"
        )


def _validate_angular(scalar: Scalar, function_name: str) -> Scalar:
    """Validate scalar has angular dimensionality and convert to radians."""
    try:
        return scalar.to("rad")
    except (ValueError, RMNError):
        raise ValueError(
            f"{function_name}() requires angular dimensionality (compatible with radians)"
        )


def _validate_dimensionless(scalar: Scalar, function_name: str) -> Scalar:
    """Validate scalar is dimensionless."""
    try:
        return scalar.to("1")
    except (ValueError, RMNError):
        raise ValueError(f"{function_name}() requires dimensionless input")


def _compute_real_or_complex(
    scalar: Scalar, real_func: Callable, complex_func: Callable
) -> Union[float, complex]:
    """Apply appropriate function based on whether scalar is real or complex."""
    value = scalar.value
    if scalar.is_complex:
        return complex_func(value)  # type: ignore
    else:
        return real_func(value)  # type: ignore


def _compute_real_or_complex_atan2(
    y: Union[float, complex], x: Union[float, complex]
) -> Union[float, complex]:
    """Compute atan2 for real or complex arguments."""
    if isinstance(y, complex) or isinstance(x, complex):
        # For complex arguments, we can't use math.atan2, use cmath.atan(y/x)
        # but adjust for quadrants if both are real
        if isinstance(y, complex) or isinstance(x, complex):
            return cmath.atan(y / x)
    return math.atan2(y, x)


# =============================================================================
# Trigonometric Functions
# =============================================================================


def sin(angular_scalar: Scalar) -> Scalar:
    """
    Compute sine of a Scalar with angular units.

    Args:
        angle_scalar (Scalar): Angle with units of rad, °, or other angular units

    Returns:
        Scalar: Dimensionless result of sin(angle)

    Examples:
        >>> result = sin(Scalar(90, "°"))    # 1.0 (dimensionless)
        >>> result = sin(Scalar(math.pi/2, "rad"))  # 1.0 (dimensionless)
        >>> result = sin(Scalar(100, "grad"))  # 1.0 (dimensionless, 100 grad = 90°)
    """
    _validate_scalar(angular_scalar, "sin")
    angle_in_rad = _validate_angular(angular_scalar, "sin")

    result_value = _compute_real_or_complex(angle_in_rad, math.sin, cmath.sin)
    return Scalar(result_value, "1")


def cos(angular_scalar: Scalar) -> Scalar:
    """
    Compute cosine of a Scalar with angular units.

    Args:
        angle_scalar (Scalar): Angle with units of rad, °, or other angular units

    Returns:
        Scalar: Dimensionless result of cos(angle)

    Examples:
        >>> result = cos(Scalar(89, "°"))    # ≈ 0.017 (dimensionless)
        >>> result = cos(Scalar(0, "rad"))   # 1.0 (dimensionless)
    """
    _validate_scalar(angular_scalar, "cos")
    angle_in_rad = _validate_angular(angular_scalar, "cos")

    result_value = _compute_real_or_complex(angle_in_rad, math.cos, cmath.cos)
    return Scalar(result_value, "1")


def tan(angular_scalar: Scalar) -> Scalar:
    """
    Compute tangent of a Scalar with angular units.

    Args:
        angle_scalar (Scalar): Angle with units of rad, °, or other angular units

    Returns:
        Scalar: Dimensionless result of tan(angle)

    Examples:
        >>> result = tan(Scalar(45, "°"))    # 1.0 (dimensionless)
        >>> result = tan(Scalar(math.pi/4, "rad"))  # 1.0 (dimensionless)
    """
    _validate_scalar(angular_scalar, "tan")
    angle_in_rad = _validate_angular(angular_scalar, "tan")

    result_value = _compute_real_or_complex(angle_in_rad, math.tan, cmath.tan)
    return Scalar(result_value, "1")


def asin(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute arcsine of a dimensionless Scalar, returning angle in radians.

    Args:
        dimensionless_scalar (Scalar): Dimensionless value between -1 and 1

    Returns:
        Scalar: Angle in radians

    Examples:
        >>> result = asin(Scalar(1.0))    # π/2 rad
        >>> result = asin(Scalar(0.5))    # π/6 rad
    """
    _validate_scalar(dimensionless_scalar, "asin")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "asin")

    result_value = _compute_real_or_complex(dimensionless, math.asin, cmath.asin)
    return Scalar(result_value, "rad")


def acos(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute arccosine of a dimensionless Scalar, returning angle in radians.

    Args:
        dimensionless_scalar (Scalar): Dimensionless value between -1 and 1

    Returns:
        Scalar: Angle in radians

    Examples:
        >>> result = acos(Scalar(0.0))    # π/2 rad
        >>> result = acos(Scalar(1.0))    # 0 rad
    """
    _validate_scalar(dimensionless_scalar, "acos")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "acos")

    result_value = _compute_real_or_complex(dimensionless, math.acos, cmath.acos)
    return Scalar(result_value, "rad")


def atan(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute arctangent of a dimensionless Scalar, returning angle in radians.

    Args:
        dimensionless_scalar (Scalar): Dimensionless value

    Returns:
        Scalar: Angle in radians

    Examples:
        >>> result = atan(Scalar(1.0))    # π/4 rad
        >>> result = atan(Scalar(0.0))    # 0 rad
    """
    _validate_scalar(dimensionless_scalar, "atan")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "atan")

    result_value = _compute_real_or_complex(dimensionless, math.atan, cmath.atan)
    return Scalar(result_value, "rad")


def atan2(y_scalar: Scalar, x_scalar: Scalar) -> Scalar:
    """
    Compute atan2(y, x) for two Scalars with compatible dimensions.

    Args:
        y_scalar (Scalar): Y coordinate (same dimensions as x_scalar)
        x_scalar (Scalar): X coordinate (same dimensions as y_scalar)

    Returns:
        Scalar: Angle in radians

    Examples:
        >>> result = atan2(Scalar(1, "m"), Scalar(1, "m"))    # π/4 rad
        >>> result = atan2(Scalar(0, "kg"), Scalar(-1, "kg"))  # π rad
    """
    _validate_scalar(y_scalar, "atan2")
    _validate_scalar(x_scalar, "atan2")

    # Extract dimensionless values (the ratio y/x will be dimensionless)
    # But we need the actual values to pass to atan2, not the scalar ratio
    # Convert both scalars to a common unit first
    try:
        y_converted = y_scalar.to(x_scalar.unit)
    except (ValueError, RMNError):
        raise ValueError("atan2 requires compatible units for y and x coordinates")

    y_value = y_converted.value
    x_value = x_scalar.value

    result_value = _compute_real_or_complex_atan2(y_value, x_value)
    return Scalar(result_value, "rad")


# =============================================================================
# Hyperbolic Functions
# =============================================================================


def sinh(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute hyperbolic sine of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input

    Returns:
        Scalar: Dimensionless result of sinh(input)
    """
    _validate_scalar(dimensionless_scalar, "sinh")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "sinh")

    result_value = _compute_real_or_complex(dimensionless, math.sinh, cmath.sinh)
    return Scalar(result_value, "1")


def cosh(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute hyperbolic cosine of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input

    Returns:
        Scalar: Dimensionless result of cosh(input)
    """
    _validate_scalar(dimensionless_scalar, "cosh")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "cosh")

    result_value = _compute_real_or_complex(dimensionless, math.cosh, cmath.cosh)
    return Scalar(result_value, "1")


def tanh(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute hyperbolic tangent of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input

    Returns:
        Scalar: Dimensionless result of tanh(input)
    """
    _validate_scalar(dimensionless_scalar, "tanh")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "tanh")

    result_value = _compute_real_or_complex(dimensionless, math.tanh, cmath.tanh)
    return Scalar(result_value, "1")


def asinh(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute inverse hyperbolic sine of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input

    Returns:
        Scalar: Dimensionless result of asinh(input)
    """
    _validate_scalar(dimensionless_scalar, "asinh")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "asinh")

    result_value = _compute_real_or_complex(dimensionless, math.asinh, cmath.asinh)
    return Scalar(result_value, "1")


def acosh(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute inverse hyperbolic cosine of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input (≥ 1)

    Returns:
        Scalar: Dimensionless result of acosh(input)
    """
    _validate_scalar(dimensionless_scalar, "acosh")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "acosh")

    result_value = _compute_real_or_complex(dimensionless, math.acosh, cmath.acosh)
    return Scalar(result_value, "1")


def atanh(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute inverse hyperbolic tangent of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input (|input| < 1)

    Returns:
        Scalar: Dimensionless result of atanh(input)
    """
    _validate_scalar(dimensionless_scalar, "atanh")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "atanh")

    result_value = _compute_real_or_complex(dimensionless, math.atanh, cmath.atanh)
    return Scalar(result_value, "1")


# =============================================================================
# Exponential and Logarithmic Functions
# =============================================================================


def exp(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute exponential (e^x) of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input

    Returns:
        Scalar: Dimensionless result of e^input

    Examples:
        >>> result = exp(Scalar(1.0))     # e ≈ 2.718 (dimensionless)
        >>> result = exp(Scalar(0.0))     # 1.0 (dimensionless)
    """
    _validate_scalar(dimensionless_scalar, "exp")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "exp")

    result_value = _compute_real_or_complex(dimensionless, math.exp, cmath.exp)
    return Scalar(result_value, "1")


def log(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute natural logarithm of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input (> 0 for real)

    Returns:
        Scalar: Dimensionless result of ln(input)

    Examples:
        >>> result = log(Scalar(math.e))  # 1.0 (dimensionless)
        >>> result = log(Scalar(1.0))     # 0.0 (dimensionless)
    """
    _validate_scalar(dimensionless_scalar, "log")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "log")

    result_value = _compute_real_or_complex(dimensionless, math.log, cmath.log)
    return Scalar(result_value, "1")


def log10(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute base-10 logarithm of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input (> 0 for real)

    Returns:
        Scalar: Dimensionless result of log₁₀(input)

    Examples:
        >>> result = log10(Scalar(100.0))  # 2.0 (dimensionless)
        >>> result = log10(Scalar(10.0))   # 1.0 (dimensionless)
    """
    _validate_scalar(dimensionless_scalar, "log10")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "log10")

    result_value = _compute_real_or_complex(dimensionless, math.log10, cmath.log10)
    return Scalar(result_value, "1")


def log2(dimensionless_scalar: Scalar) -> Scalar:
    """
    Compute base-2 logarithm of a dimensionless Scalar.

    Args:
        dimensionless_scalar (Scalar): Dimensionless input (> 0 for real)

    Returns:
        Scalar: Dimensionless result of log₂(input)

    Examples:
        >>> result = log2(Scalar(8.0))    # 3.0 (dimensionless)
        >>> result = log2(Scalar(2.0))    # 1.0 (dimensionless)
    """
    _validate_scalar(dimensionless_scalar, "log2")
    dimensionless = _validate_dimensionless(dimensionless_scalar, "log2")

    # Use change of base formula: log₂(x) = ln(x) / ln(2)
    if dimensionless_scalar.is_complex:
        result_value = cmath.log(dimensionless.value) / cmath.log(2)
    else:
        result_value = math.log2(dimensionless.value)

    return Scalar(result_value, "1")


# =============================================================================
# Power Functions
# =============================================================================


def sqrt(scalar: Scalar) -> Scalar:
    """
    Compute square root of a Scalar.

    The units are also square-rooted (e.g., √(m²) = m).

    Args:
        scalar (Scalar): Input scalar

    Returns:
        Scalar: Square root with appropriate units

    Examples:
        >>> result = sqrt(Scalar(4, "m^2"))   # 2.0 m
        >>> result = sqrt(Scalar(9.0))        # 3.0 (dimensionless)
    """
    _validate_scalar(scalar, "sqrt")
    return scalar.nth_root(2)


def cbrt(scalar: Scalar) -> Scalar:
    """
    Compute cube root of a Scalar.

    The units are also cube-rooted (e.g., ∛(m³) = m).

    Args:
        scalar (Scalar): Input scalar

    Returns:
        Scalar: Cube root with appropriate units

    Examples:
        >>> result = cbrt(Scalar(8, "m^3"))   # 2.0 m
        >>> result = cbrt(Scalar(27.0))       # 3.0 (dimensionless)
    """
    _validate_scalar(scalar, "cbrt")
    return scalar.nth_root(3)


def pow(scalar: Scalar, exponent: Union[int, float]) -> Scalar:
    """
    Compute scalar raised to the power of exponent.

    Args:
        scalar (Scalar): Base value
        exponent (int or float): Exponent (must be numeric, not Scalar)

    Returns:
        Scalar: scalar^exponent with appropriate units

    Examples:
        >>> result = pow(Scalar(2, "m"), 3)   # 8.0 m³
        >>> result = pow(Scalar(4.0), 0.5)    # 2.0 (dimensionless)
    """
    _validate_scalar(scalar, "pow")
    return scalar**exponent


# =============================================================================
# Constants
# =============================================================================

# Mathematical constants as Scalar objects
pi = Scalar(math.pi, "rad")  # π radians
e = Scalar(math.e)  # Euler's number (dimensionless)
tau = Scalar(2 * math.pi, "rad")  # τ = 2π radians
