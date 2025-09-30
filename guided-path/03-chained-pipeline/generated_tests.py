import pytest
import math
from importlib import import_module

def _resolve_target(target_spec):
    module, func = target_spec.split(":")
    return getattr(import_module(module), func)

def isinstance_complex(value):
    return isinstance(value, complex)

def test_divide_by_infinity():
    f = _resolve_target("division:divide")
    assert abs(f(1.0, float('inf')) - 0.0) <= 1e-10

def test_divide_by_negative_infinity():
    f = _resolve_target("division:divide")
    assert abs(f(1.0, float('-inf')) - 0.0) <= 1e-10

def test_divide_by_zero():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(1.0, 0.0)

def test_divide_infinity_by_infinity():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('inf'), float('inf')))

def test_divide_infinity_by_negative_infinity():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('inf'), float('-inf')))

def test_divide_infinity_by_positive():
    f = _resolve_target("division:divide")
    assert math.isinf(f(float('inf'), 1.0))

def test_divide_nan_by_nan():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('nan'), float('nan')))

def test_divide_nan_by_number():
    f = _resolve_target("division:divide")
    assert math.isnan(f(float('nan'), 1.0))

def test_divide_negative_by_negative():
    f = _resolve_target("division:divide")
    assert abs(f(-10.0, -2.0) - 5.0) <= 1e-10

def test_divide_negative_by_positive():
    f = _resolve_target("division:divide")
    assert abs(f(-10.0, 2.0) - -5.0) <= 1e-10

def test_divide_negative_infinity_by_positive():
    f = _resolve_target("division:divide")
    assert math.isinf(f(float('-inf'), 1.0))

def test_divide_negative_infinity_by_zero():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(float('-inf'), 0.0)

def test_divide_number_by_nan():
    f = _resolve_target("division:divide")
    assert math.isnan(f(1.0, float('nan')))

def test_divide_positive_by_negative():
    f = _resolve_target("division:divide")
    assert abs(f(10.0, -2.0) - -5.0) <= 1e-10

def test_divide_positive_infinity_by_zero():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(float('inf'), 0.0)

def test_divide_very_large_by_very_small():
    f = _resolve_target("division:divide")
    assert math.isinf(f(1e+308, 1e-308))

def test_divide_very_small_by_very_large():
    f = _resolve_target("division:divide")
    assert abs(f(1e-308, 1e+308) - 0.0) <= 1e-10

def test_divide_zero_by_zero():
    f = _resolve_target("division:divide")
    with pytest.raises(ZeroDivisionError):
        f(0.0, 0.0)
