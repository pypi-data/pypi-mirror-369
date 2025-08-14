from typing import Iterable

import sympy as sp

from smitfit.expr import Expr, as_expr
from smitfit.model import _define_parameters
from smitfit.parameter import Parameters
from smitfit.typing import Numerical


# TODO y is not used?
class Function:
    def __init__(
        self, func: Expr | sp.Expr | dict[sp.Symbol, sp.Expr] | str, y=sp.Symbol("y")
    ) -> None:
        if isinstance(func, dict):
            assert len(func) == 1
            self.y = list(func.keys())[0]
            self.expr = as_expr(list(func.values())[0])
        elif isinstance(func, str):
            eq = sp.parse_expr(func, evaluate=False)
            if isinstance(eq, sp.Expr):
                self.y = y
                self.expr = as_expr(eq)
            elif isinstance(eq, sp.Equality):
                assert isinstance(eq.lhs, sp.Symbol)
                self.y = eq.lhs
                self.expr = as_expr(eq.rhs)
            else:
                raise ValueError("Invalid string expression")
        elif isinstance(func, sp.Expr):
            self.y = y
            self.expr = as_expr(func)
        elif isinstance(func, Expr):
            self.y = y
            self.expr = func

    def __call__(self, **kwargs):
        return self.expr(**kwargs)  # type: ignore

    @property
    def x_symbols(self) -> set[sp.Symbol]:
        return self.expr.symbols

    @property
    def y_symbols(self) -> set[sp.Symbol]:
        return set([self.y])

    # #TODO copy/paste code with Model -> baseclass?
    def define_parameters(
        self, parameters: dict[str, Numerical] | Iterable[str] | str = "*"
    ) -> Parameters:
        symbol_names = {s.name for s in self.x_symbols}
        return _define_parameters(parameters, symbol_names)
