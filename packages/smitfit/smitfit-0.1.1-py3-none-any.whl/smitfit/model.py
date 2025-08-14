from __future__ import annotations

import re
from fnmatch import fnmatch
from typing import Iterable, cast

import sympy as sp
from toposort import toposort

from smitfit.expr import Expr, _parse_subs_args, as_expr
from smitfit.parameter import Parameter, Parameters
from smitfit.typing import Numerical


def parse_model_str(model: Iterable[str]) -> dict[sp.Symbol, sp.Expr]:
    model_dict = {}
    for s in model:
        eq = sp.parse_expr(s, evaluate=False)
        if not isinstance(eq.lhs, sp.Symbol):
            raise ValueError("lhs must be a symbol")
        if not isinstance(eq.rhs, sp.Expr):
            raise ValueError("rhs must be an expression")

        model_dict[eq.lhs] = eq.rhs

    return model_dict


class Model:
    def __init__(self, model: dict[sp.Symbol, sp.Expr | Expr] | Iterable[str] | str) -> None:
        if isinstance(model, dict):
            self.model = cast(dict[sp.Symbol, sp.Expr | Expr], model)
        elif isinstance(model, str):
            self.model = parse_model_str([model])
        elif isinstance(model, Iterable):
            self.model = parse_model_str(model)
        else:
            raise ValueError("Invalid type")

        self.expr: dict = {k: as_expr(v) for k, v in self.model.items()}
        topology = {k: v.symbols for k, v in self.expr.items()}
        self.call_stack = [
            elem for subset in toposort(topology) for elem in subset if elem in self.model.keys()
        ]

    @property
    def x_symbols(self) -> set[sp.Symbol]:
        return set.union(*(v.symbols for v in self.expr.values())) - self.y_symbols

    @property
    def y_symbols(self) -> set[sp.Symbol]:
        return set(self.model.keys())

    def __call__(self, **kwargs):
        resolved = {}
        for key in self.call_stack:
            resolved[key.name] = self.expr[key](**kwargs, **resolved)
        return resolved

    # TODO copy/paste code with Function -> baseclass
    def define_parameters(
        self, parameters: dict[str, Numerical] | Iterable[str] | str = "*"
    ) -> Parameters:
        symbol_names = {s.name for s in self.x_symbols}
        return _define_parameters(parameters, symbol_names)

    def subs(self, *args, **kwargs) -> Model:
        """
        Substitute symbols in the model with other symbols or expressions.

        Works similar to sympy's subs() method. Returns a new Model instance.

        Args:
            *args: Can be a dict, list, or tuple of (old, new) pairs
            **kwargs: Can be symbol names and their replacements

        Returns:
            A new Model with substituted expressions
        """
        # Get all relevant symbols from the model
        all_symbols = self.x_symbols.union(self.y_symbols)

        # Parse substitution arguments
        subs_dict = _parse_subs_args(*args, symbols=all_symbols, **kwargs)
        # Create new model with substitutions
        new_model = {}
        for symbol, expr in self.model.items():
            if isinstance(expr, (sp.Expr, sp.MatrixBase, Expr)):
                new_expr = expr.subs(subs_dict)
            else:
                new_expr = expr

            new_model[symbol] = new_expr

        return Model(new_model)


def _define_parameters(
    parameters: dict[str, Numerical] | Iterable[str] | str, symbol_names: set[str]
) -> Parameters:
    if parameters == "*":
        params = [Parameter(name) for name in symbol_names]
    elif isinstance(parameters, str):
        if "*" in parameters:  # fnmatch
            params = [Parameter(name) for name in symbol_names if fnmatch(name, parameters)]
        else:
            # split by comma, whiteplace, etc
            params = [Parameter(k.strip()) for k in re.split(r"[,;\s]+", parameters)]

    elif isinstance(parameters, dict):
        params = [Parameter(k, guess=v) for k, v in parameters.items() if k in symbol_names]
    elif isinstance(parameters, Iterable):
        params = [Parameter(k) for k in parameters if k in symbol_names]
    else:
        raise TypeError("Invalid type")

    return Parameters(params)
