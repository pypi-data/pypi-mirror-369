from smitfit.expr import as_expr
from smitfit.composite_expr import CompositeExpr
from operator import add, mul, truediv, sub
from functools import reduce


class Add(CompositeExpr):
    def __init__(self, *args):
        expr = {f"arg_{i}": as_expr(arg) for i, arg in enumerate(args)}
        super().__init__(expr)

    def __call__(self, **kwargs):
        return reduce(add, [v(**kwargs) for v in self.expr.values()])


class Mul(CompositeExpr):
    def __init__(self, *args):
        expr = {f"arg_{i}": as_expr(arg) for i, arg in enumerate(args)}
        super().__init__(expr)

    def __call__(self, **kwargs):
        return reduce(mul, [v(**kwargs) for v in self.expr.values()])


class Div(CompositeExpr):
    def __init__(self, nom, denom):
        expr = {"nom": as_expr(nom), "denom": as_expr(denom)}
        super().__init__(expr)

    def __call__(self, **kwargs):
        components = super().__call__(**kwargs)
        return components["nom"] / components["denom"]


class Sub(CompositeExpr):
    def __init__(self, a, b):
        expr = {"a": as_expr(a), "b": as_expr(b)}
        super().__init__(expr)

    def __call__(self, **kwargs):
        components = super().__call__(**kwargs)
        return components["a"] - components["b"]
