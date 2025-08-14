# %%
from __future__ import annotations

from functools import cached_property
from typing import Any, Callable, Iterable, Union, Mapping, Dict, Set, Tuple, Optional

import numpy as np
import sympy as sp
from smitfit.typing import Numerical


def _parse_subs_args(
    *args, symbols: Optional[Set[sp.Symbol]] = None, **kwargs
) -> Dict[sp.Symbol, Any]:
    """
    Helper function to parse substitution arguments in a consistent way.

    Args:
        *args: Either a dict or a sequence of (old, new) pairs, or a single (old, new) pair
        symbols: Optional set of symbols to match names against for keyword arguments
        **kwargs: Symbol names and their replacements

    Returns:
        Dict mapping symbols to their replacements
    """
    subs_dict = {}

    # Handle dict or sequence of (old, new) pairs in args
    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, Mapping):
            subs_dict.update(arg)
        elif isinstance(arg, (list, tuple)):
            for old, new in arg:
                subs_dict[old] = new
    elif len(args) == 2:  # Handle direct (old, new) pair
        subs_dict[args[0]] = args[1]

    # Handle keyword arguments
    for name, replacement in kwargs.items():
        if symbols:
            # Try to find a symbol with this name
            matching_symbols = [s for s in symbols if s.name == name]
            if matching_symbols:
                subs_dict[matching_symbols[0]] = replacement
                continue

        # Create a new symbol if none exists (consistent with sympy behavior)
        subs_dict[sp.Symbol(name)] = replacement

    return subs_dict


# %%
class Expr:
    def __init__(self, expr) -> None:
        self._expr = expr

    @property
    def expr(self):
        return self._expr

    @cached_property
    def symbols(self) -> set[sp.Symbol]:
        return set()

    def filter_kwargs(self, **kwargs) -> dict[str, Numerical]:
        """Parse kwargs and take only the ones in `free_parameters`"""
        try:
            kwargs = {k: kwargs[k] for k in {s.name for s in self.symbols}}
        except KeyError as e:
            raise KeyError(f"Missing value for {e}") from e

        return kwargs

    def __getitem__(self, item):
        return GetItem(self, item)

    def __add__(self, other):
        from smitfit.operator import Add

        return Add(self, other)

    def __call__(self, **kwargs):
        return self._expr

    def subs(self, *args, **kwargs) -> Expr:
        """
        Base substitution method. By default, returns a copy of self since
        generic expressions don't have symbols to substitute.

        Args:
            *args: Either a dict or a sequence of (old, new) pairs, or a single (old, new) pair
            **kwargs: Symbol names and their replacements

        Returns:
            A new expression with substitutions applied
        """
        # Default implementation just returns a copy
        return type(self)(self._expr)


class GetItem(Expr):
    def __init__(self, expr: Expr, item: Union[tuple, slice, int]):
        # todo super
        self._expr = expr
        self.item = item

    def __call__(self, **kwargs):
        ans = self._expr(**kwargs)
        return ans[self.item]

    @cached_property
    def symbols(self) -> set[sp.Symbol]:
        return self._expr.symbols

    def __repr__(self) -> str:
        return f"{self.expr.__repr__()}[{self.item!r}]"

    def subs(self, *args, **kwargs) -> Expr:
        """
        Applies substitutions to the underlying expression and preserves the getitem operation.
        """
        return GetItem(self._expr.subs(*args, **kwargs), self.item)


class SympyExpr(Expr):
    @cached_property
    def symbols(self) -> set[sp.Symbol]:
        return self._expr.free_symbols

    @cached_property
    def lambdified(self) -> Callable:
        ld = sp.lambdify(sorted(self.symbols, key=str), self._expr)

        return ld

    def __repr__(self) -> str:
        return f"SympyExpr({self._expr})"

    def __call__(self, **kwargs):
        return self.lambdified(**self.filter_kwargs(**kwargs))

    def subs(self, *args, **kwargs) -> SympyExpr:
        """
        Substitute symbols in the expression with other symbols or expressions.

        Works similar to sympy's subs() method.

        Args:
            *args: Can be a dict, list, or tuple of (old, new) pairs, or a single (old, new) pair
            **kwargs: Can be symbol names and their replacements

        Returns:
            A new SympyExpr with substituted expressions
        """
        subs_dict = _parse_subs_args(*args, symbols=self.symbols, **kwargs)
        return SympyExpr(self._expr.subs(subs_dict))


class SympyMatrixExpr(Expr):
    def __init__(self, expr: sp.MatrixBase) -> None:
        super().__init__(expr)

    @cached_property
    def symbols(self) -> set[sp.Symbol]:
        return self._expr.free_symbols

    @cached_property
    def lambdified(self) -> dict[tuple[int, int], Callable]:
        lambdas = {}
        for i, j in np.ndindex(self.expr.shape):
            lambdas[(i, j)] = sp.lambdify(sorted(self.symbols, key=str), self.expr[i, j])

        return lambdas

    def __call__(self, **kwargs):
        # when marix elements != scalars, shape is expanded by the first dimensions to accomodate.
        ld_kwargs = self.filter_kwargs(**kwargs)

        base_shape = np.broadcast_shapes(
            *(getattr(value, "shape", tuple()) for value in ld_kwargs.values())
        )

        # squeeze last dim if shape is (1,)
        base_shape = () if base_shape == (1,) else base_shape
        shape = base_shape + self.expr.shape

        out = np.empty(shape)
        for i, j in np.ndindex(self.expr.shape):
            out[..., i, j] = self.lambdified[i, j](**ld_kwargs)

        return out

    def subs(self, *args, **kwargs) -> SympyMatrixExpr:
        """
        Substitute symbols in the matrix expression with other symbols or expressions.

        Works similar to sympy's subs() method.

        Args:
            *args: Can be a dict, list, or tuple of (old, new) pairs, or a single (old, new) pair
            **kwargs: Can be symbol names and their replacements

        Returns:
            A new SympyMatrixExpr with substituted expressions
        """
        subs_dict = _parse_subs_args(*args, symbols=self.symbols, **kwargs)
        return SympyMatrixExpr(self._expr.subs(subs_dict))


class CustomFunction(Expr):
    def __init__(self, func: Callable, symbols: Iterable[sp.Symbol]):
        self.func = func
        self.symbols = set(symbols)

    def __call__(self, **kwargs):
        return self.func(**kwargs)

    def subs(self, *args, **kwargs) -> CustomFunction:
        """
        Substitute symbols in the custom function with other symbols or expressions.
        Has no effect !!

        Returns:
            A new CustomFunction with substituted expressions
        """
        return CustomFunction(self.func, self.symbols)


def str_to_expr(s: str) -> SympyExpr:
    sp_expr = sp.parse_expr(s, evaluate=False)
    if isinstance(sp_expr, sp.Equality):  # this is a special case for root finding
        return SympyExpr(sp_expr.lhs - sp_expr.rhs)  # type: ignore
    elif isinstance(sp_expr, sp.Expr):
        return SympyExpr(sp_expr)
    else:
        raise ValueError(f"Invalid string expression: {s!r}")


def as_expr(expr: Any) -> Expr:
    if isinstance(expr, Expr):
        return expr
    elif isinstance(expr, str):
        return str_to_expr(expr)
    elif isinstance(expr, (float, int, np.ndarray)):  # torch tensor, ...
        return Expr(expr)
    elif isinstance(expr, sp.MatrixBase):
        return SympyMatrixExpr(expr)
    if isinstance(expr, sp.Expr):
        return SympyExpr(expr)
    elif isinstance(expr, dict):
        raise DeprecationWarning("To convert dicts, pass values to `as_expr` individually")
    else:
        raise TypeError(f"Invalid type: {type(expr)}")
