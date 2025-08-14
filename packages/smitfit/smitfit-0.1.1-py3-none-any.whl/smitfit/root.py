from functools import partial
import numpy as np

from smitfit.parameter import pack, unpack
from smitfit.expr import as_expr


class Root:
    def __init__(self, eqns: list) -> None:
        self.expr: list = [as_expr(e) for e in eqns]
        self.guess = {}
        self.params = {}

    def set_x0(self, guess: dict):
        self.guess = guess

    def set_args(self, params: dict):
        self.params = params

    @property
    def x0(self) -> np.ndarray:
        return pack(self.guess.values())

    @property
    def args(self) -> tuple:
        return tuple(self.params.values())

    @property
    def func(self):
        unpack_x0 = partial(unpack, shapes={k: (1,) for k in self.guess})

        def unpack_args(args):
            return {n: arg for n, arg in zip(self.params, args)}

        def callable(x0, *args):
            ans = [e(**unpack_x0(x0), **unpack_args(args)) for e in self.expr]
            return np.concatenate([arr.flatten() for arr in ans])

        return callable
