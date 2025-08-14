from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Iterable, Optional
from scipy.optimize import Bounds

import numpy as np
import numpy.typing as npt
import sympy as sp

from smitfit.typing import Numerical


@dataclass
class Parameter:
    """A mutable parameter class that supports method chaining"""

    name: str
    guess: Numerical = 1.0
    lower_bound: Optional[Numerical] = None
    upper_bound: Optional[Numerical] = None
    fixed: bool = False  # TODO fixed per array element?

    @property
    def symbol(self) -> sp.Symbol:
        return sp.Symbol(self.name)

    @property
    def shape(self) -> tuple[int, ...]:
        shape = getattr(self.guess, "shape", tuple())
        return shape

    @property
    def bounds(self) -> tuple[Optional[Numerical], Optional[Numerical]]:
        return self.lower_bound, self.upper_bound

    def fix(self) -> Parameter:
        """Fix the parameter at its current guess value"""
        self.fixed = True
        return self

    def unfix(self) -> Parameter:
        """Make the parameter free to vary"""
        self.fixed = False
        return self

    def set_bounds(
        self, lower_bound: Optional[Numerical] = None, upper_bound: Optional[Numerical] = None
    ) -> Parameter:
        """Set parameter bounds"""
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        return self

    def set_positive(self) -> Parameter:
        """Set positive bounds"""
        self.lower_bound = 0
        return self

    def set_negative(self) -> Parameter:
        """Set negative bounds"""
        self.upper_bound = 0
        return self

    def set_guess(self, value: Numerical) -> Parameter:
        """Set initial guess value"""
        self.guess = value
        return self


class Parameters:
    """Container for managing multiple parameters"""

    def __init__(self, parameters: Iterable[Parameter]):
        self._parameters = {p.name: p for p in parameters}

    def __getitem__(self, key: str) -> Parameter:
        return self._parameters[key]

    def __iter__(self):
        return iter(self._parameters.values())

    def __len__(self):
        return len(self._parameters)

    def __add__(self, other: Parameters) -> Parameters:
        return Parameters(self.to_list() + other.to_list())

    @classmethod
    def from_guess(
        cls,
        guess: dict[str, Numerical],
    ) -> Parameters:
        return cls([Parameter(name, guess=guess) for name, guess in guess.items()])

    @classmethod
    def from_names(
        cls,
        names: Iterable[str],
    ) -> Parameters:
        return cls([Parameter(name) for name in names])

    @property
    def symbols(self) -> set[sp.Symbol]:
        return {p.symbol for p in self}

    @property
    def guess(self) -> dict[str, Numerical]:  # other types?
        return {p.name: np.asarray(p.guess) for p in self}

    @property
    def shapes(self) -> dict[str, tuple]:
        return {p.name: p.shape for p in self}

    def fix(self, *names: str) -> Parameters:
        """Fix specified parameters"""
        if not names:
            names = tuple(self._parameters.keys())
        for name in names:
            self._parameters[name].fix()
        return self

    def unfix(self, *names: str) -> Parameters:
        """Unfix specified parameters"""
        if not names:
            names = tuple(self._parameters.keys())
        for name in names:
            self._parameters[name].unfix()
        return self

    def set_bounds(
        self, bounds_dict: dict[str, tuple[Optional[Numerical], Optional[Numerical]]]
    ) -> Parameters:
        """Set bounds for multiple parameters at once"""
        for name, (lower, upper) in bounds_dict.items():
            self._parameters[name].set_bounds(lower, upper)
        return self

    def set_positive(self, *names: str) -> Parameters:
        """Set positive bounds for specified parameters"""
        if not names:
            names = tuple(self._parameters.keys())
        for name in names:
            self._parameters[name].set_bounds(0, None)
        return self

    def set_negative(self, *names: str) -> Parameters:
        """Set negative bounds for specified parameters"""
        if not names:
            names = tuple(self._parameters.keys())
        for name in names:
            self._parameters[name].set_bounds(None, 0)
        return self

    def set_guesses(self, guess_dict: dict[str, Numerical]) -> Parameters:
        """Set initial guesses for multiple parameters at once"""
        for name, guess in guess_dict.items():
            self._parameters[name].set_guess(guess)
        return self

    @property
    def fixed(self) -> Parameters:
        """Get list of fixed parameters"""
        return Parameters([p for p in self._parameters.values() if p.fixed])

    @property
    def free(self) -> Parameters:
        """Get list of free parameters"""
        return Parameters([p for p in self._parameters.values() if not p.fixed])

    def to_list(self) -> list[Parameter]:
        """Convert to parameter list"""
        return list(self._parameters.values())

    def to_dataframe(self):
        """Convert parameters to a DataFrame.

        Returns a DataFrame from polars or pandas, depending on which is installed.
        Prioritizes polars over pandas.
        """
        data = [asdict(p) for p in self]

        try:
            import polars as pl  # type: ignore

            return pl.DataFrame(data)
        except ImportError:
            try:
                import pandas as pd  # type: ignore

                return pd.DataFrame(data)
            except ImportError:
                raise ImportError(
                    "Neither polars nor pandas is installed. Please install one of them."
                )

    def copy(self) -> Parameters:
        return Parameters([replace(p) for p in self])

    def __repr__(self) -> str:
        return f"Parameters({list(self._parameters.values())})"


def unpack(x: npt.ArrayLike, shapes: dict[str, tuple[int, ...]]) -> dict[str, np.ndarray]:
    """Unpack a ndim 1 array of concatenated parameter values into a dictionary of
    parameter name: parameter_value where parameter values are cast back to their
    specified shapes.
    """
    sizes = [int(np.prod(shape)) for shape in shapes.values()]

    x_split = np.split(x, np.cumsum(sizes))
    p_values = {name: arr.reshape(shape) for (name, shape), arr in zip(shapes.items(), x_split)}

    return p_values


def pack(
    parameter_values: Iterable[Numerical],
) -> np.ndarray:  # todo iterable numerical dtype input
    """Pack a dictionary of parameter_name together as array"""

    return np.concatenate(tuple(np.array(param_value).ravel() for param_value in parameter_values))


def scipy_bounds(parameters: Parameters) -> Optional[Bounds]:
    lb, ub = [], []
    for p in parameters:
        size = np.prod(p.shape, dtype=int)
        lb += [p.lower_bound] * size
        ub += [p.upper_bound] * size

    if all(elem is None for elem in lb + ub):
        return None
    else:
        lb = [-np.inf if elem is None else elem for elem in lb]
        ub = [np.inf if elem is None else elem for elem in ub]
        return Bounds(lb, ub)  # type: ignore
