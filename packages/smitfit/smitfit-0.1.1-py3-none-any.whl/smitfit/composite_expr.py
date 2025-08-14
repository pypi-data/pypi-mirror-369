from __future__ import annotations

from functools import cached_property
from typing import Optional, Dict, Any

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from smitfit.expr import Expr, _parse_subs_args, as_expr


class CompositeExpr(Expr):
    @cached_property
    def symbols(self) -> set[sp.Symbol]:
        return set().union(*(expr.symbols for expr in self.expr.values()))

    def __call__(self, **kwargs):
        return {k: v(**kwargs) for k, v in self.expr.items()}

    def subs(self, *args, **kwargs) -> CompositeExpr:
        """
        Substitute symbols in all component expressions with other symbols or expressions.

        Args:
            *args: Can be a dict, list, or tuple of (old, new) pairs, or a single (old, new) pair
            **kwargs: Can be symbol names and their replacements

        Returns:
            A new CompositeExpr with substituted expressions
        """
        subs_dict = _parse_subs_args(*args, symbols=self.symbols, **kwargs)

        # Create new substituted expressions
        new_expr = {k: v.subs(subs_dict) for k, v in self.expr.items()}

        # Create a new instance with the same class as self
        # This preserves the specific CompositeExpr subclass type
        result = type(self).__new__(type(self))
        result._expr = new_expr

        # Copy any other important attributes
        for attr_name in self.__dict__:
            if attr_name != "_expr" and attr_name != "symbols":
                setattr(result, attr_name, getattr(self, attr_name))

        return result


class MarkovIVP(CompositeExpr):
    """Uses scipy.integrate.solve_ivp to numerically find time evolution of a markov process
        given a transition rate matrix.

    Returned shape is <states>, <datapoints>

    """

    def __init__(
        self,
        t: sp.Symbol | sp.Expr | Expr,
        trs_matrix: sp.Matrix | Expr,
        y0: sp.Matrix | Expr,
        domain: Optional[tuple[float, float]] = None,
        **ivp_kwargs,
    ):
        d = {"t": t, "trs_matrix": trs_matrix, "y0": y0}
        expr = {k: as_expr(v) for k, v in d.items()}
        super().__init__(expr)

        ivp_defaults = {"method": "Radau"}
        self.ivp_defaults = ivp_defaults | ivp_kwargs
        self.domain = domain

    def __call__(self, **kwargs):
        components = super().__call__(**kwargs)

        # if `self['t']` does not depend on any parameters; domain can be precomputed and
        # does not have to be determined for every call
        # although its every fast to do so
        domain = self.domain or self.get_domain(components["t"])
        sol = solve_ivp(
            self.grad_func,
            domain,
            y0=components["y0"].squeeze(),
            t_eval=components["t"],
            args=(components["trs_matrix"],),
            **self.ivp_defaults,
        )

        return sol.y

    def get_domain(self, arr: np.ndarray) -> tuple[float, float]:
        # padding?
        return arr[0], arr[-1]

    @staticmethod
    def grad_func(t, y, trs_matrix):
        return trs_matrix @ y
