from smitfit.operator import Add, Mul
from smitfit.expr import Expr, SympyExpr
import numpy as np
import sympy as sp


def test_add():
    add_expr = Add(1, 2, 3)
    result = add_expr()
    assert result == 6

    add_expr = Add(1, Add(2, 3))
    result = add_expr()
    assert result == 6

    add_expr = Add(1, Mul(2, 3))
    result = add_expr()
    assert result == 7

    arr = np.random.rand(10)
    add_expr = Expr(arr) + SympyExpr(sp.Symbol("a"))
    assert np.allclose(add_expr(a=3), arr + 3)


def test_mul():
    mul_expr = Mul(1, 2, 3)
    result = mul_expr()
    assert result == 6

    mul_expr = Mul(1, Mul(2, 3))
    result = mul_expr()
    assert result == 6

    mul_expr = Mul(2, Add(2, 3))
    result = mul_expr()
    assert result == 10
