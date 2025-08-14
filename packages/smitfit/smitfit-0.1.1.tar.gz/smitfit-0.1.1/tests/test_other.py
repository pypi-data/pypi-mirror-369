from smitfit.model import Model
import sympy as sp
from smitfit.expr import Expr
import numpy as np
from smitfit.function import Function


def test_model_from_str():
    model = Model("y == a * x + b")
    assert model.y_symbols == {sp.Symbol("y")}
    assert model.x_symbols == {sp.Symbol("x"), sp.Symbol("a"), sp.Symbol("b")}

    lhs = model.model[sp.Symbol("y")]
    rhs = sp.Add(sp.Mul(sp.Symbol("a"), sp.Symbol("x")), sp.Symbol("b"))
    assert sp.Equality(lhs, rhs)


# move to model tests
def test_model_parameters():
    model = Model("y == a * x + b")
    params = model.define_parameters()
    assert len(params) == 3
    assert {p.name for p in params} == {"a", "b", "x"}

    params = model.define_parameters({"a": 3, "b": 4, "c": 5})
    assert len(params) == 2
    assert {p.name for p in params} == {"a", "b"}
    assert params["a"].guess == 3
    assert params["b"].guess == 4


def test_func_expr():
    arr = np.random.rand(3, 4)
    func = Function(Expr(arr))

    assert np.allclose(func(), arr)
