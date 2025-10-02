import pytest
import math
from importlib import import_module

def _resolve_target(target_spec):
    module, func = target_spec.split(":")
    return getattr(import_module(module), func)

def isinstance_complex(value):
    return isinstance(value, complex)

def test_both_negative():
    f = _resolve_target("division:divide")
    assert abs(f(-10, -2) - 5.0) <= 1e-10

def test_infinity_denominator():
    f = _resolve_target("division:divide")
    assert abs(f(10, float('inf')) - 0.0) <= 1e-10

def test_infinity_numerator():
    f = _resolve_target("division:divide")
    assert math.isinf(f(float('inf'), 2))

def test_nan_denominator():
    f = _resolve_target("division:divide")
    assert math.isnan(f(10, float('nan')))

def test_nan_numerator():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('nan'), 2))

def test_negative_denominator():
    f = _resolve_target("division:divide")
    assert abs(f(10, -2) - -5.0) <= 1e-10

def test_negative_infinity_numerator():
    f = _resolve_target("division:divide")
    assert math.isinf(f(float('-inf'), 2))

def test_negative_numerator():
    f = _resolve_target("division:divide")
    assert abs(f(-10, 2) - -5.0) <= 1e-10

def test_negative_zero_denominator():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(5, -0.0)

def test_non_numeric_both_args():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f('a', 'b')

def test_non_numeric_first_arg_string():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f('5', 2)

def test_non_numeric_second_arg_string():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f(10, '2')

def test_none_first_arg():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f(None, 5)

def test_none_second_arg():
    f = _resolve_target("division:divide")
    with pytest.raises(TypeError):
        f(10, None)

def test_very_large_numerator():
    f = _resolve_target("division:divide")
    assert abs(f(1e+308, 2) - 5e+307) <= 1e+297

def test_very_small_denominator():
    f = _resolve_target("division:divide")
    assert abs(f(1, 1e-308) - 1e+308) <= 1e+298

def test_zero_division():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(1, 0)

def test_zero_division_float():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(1.5, 0.0)
