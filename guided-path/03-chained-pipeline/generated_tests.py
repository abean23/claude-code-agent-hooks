import pytest
import math
from importlib import import_module

def _resolve_target(target_spec):
    module, func = target_spec.split(":")
    return getattr(import_module(module), func)

def test_divide_by_zero():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(10, 0)

def test_divide_by_zero_negative():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(-5, 0)

def test_divide_by_zero_float():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(3.5, 0.0)

def test_type_error_string_numerator():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f('10', 2)

def test_type_error_string_denominator():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f(10, '2')

def test_type_error_none_numerator():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f(None, 5)

def test_type_error_none_denominator():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f(10, None)

def test_infinity_numerator():
    f = _resolve_target("division:divide")
    assert math.isinf(f(float('inf'), 2))

def test_infinity_denominator():
    f = _resolve_target("division:divide")
    assert f(10, float('inf')) == 0.0

def test_negative_infinity_numerator():
    f = _resolve_target("division:divide")
    assert math.isinf(f(float('-inf'), 2))

def test_nan_numerator():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('nan'), 2))

def test_nan_denominator():
    f = _resolve_target("division:divide")
    assert math.isnan(f(10, float('nan')))

def test_infinity_by_infinity():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('inf'), float('inf')))

def test_positive_division():
    f = _resolve_target("division:divide")
    assert f(10, 2) == 5.0

def test_negative_division():
    f = _resolve_target("division:divide")
    assert f(-10, 2) == -5.0

def test_float_division():
    f = _resolve_target("division:divide")
    assert f(7.5, 2.5) == 3.0

def test_integer_result_from_floats():
    f = _resolve_target("division:divide")
    assert f(10.0, 5.0) == 2.0
