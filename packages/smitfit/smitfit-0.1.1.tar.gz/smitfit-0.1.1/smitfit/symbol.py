from typing import Optional

import numpy as np
import numpy.typing as npt
import sympy as sp


class Symbols(dict):
    def __init__(self, names, cls=sp.Symbol, **kwargs):
        default_kwargs = {"seq": True}
        default_kwargs.update(kwargs)
        super().__init__({s.name: s for s in sp.symbols(names, cls=cls, **default_kwargs)})

    def __repr__(self):
        return f"Symbols({list(self.keys())})"

    def __getattr__(self, name) -> sp.Symbol:
        if name in self:
            return self[name]
        raise AttributeError(f"'SymbolNamespace' object has no attribute '{name}'")


def symbol_matrix(
    name: Optional[str] = None,
    shape: Optional[tuple[int, ...]] = None,
    names: Optional[list[str]] = None,
    suffix: Optional[list[str]] = None,
) -> sp.Matrix:
    if shape is None:
        if names is not None:
            shape = (len(names), 1)
        elif suffix is not None:
            shape = (len(suffix), 1)
        else:
            raise ValueError("If 'shape' is not given, must specify 'names' or 'suffix'")

    # Generate names for parameters. Uses 'names' first, then <name>_<suffix> otherwise generates suffices
    # from indices
    if names is None and name is None:
        raise ValueError("Must specify either 'name' or 'names'")
    elif names is None:
        name_arr = np.full(shape, fill_value="", dtype=object)
        if suffix is None:
            for i, j in np.ndindex(shape):
                name_arr[i, j] = f"{name}_{i}_{j}"
        else:
            suffix_arr = np.array(suffix).reshape(shape)
            for i, j in np.ndindex(shape):
                name_arr[i, j] = f"{name}_{suffix_arr[i, j]}"
    else:
        name_arr = np.array(names).reshape(shape)

    matrix = sp.zeros(*shape)
    for i, j in np.ndindex(shape):
        matrix[i, j] = sp.Symbol(
            name=name_arr[i, j],
        )

    return matrix


# def get_symbols(*symbolic_objects) -> dict[str, Symbol]:
#     """Returns a dictionary of symbols
#     if no object is given, only returns FitSymbols
#     otherwise returns dict of symbols in the object
#     """
#     if len(symbolic_objects) == 0:
#         return FitSymbol._instances
#     else:
#         symbols = set()
#         for symbolic_object in symbolic_objects:
#             if isinstance(symbolic_object, dict):
#                 symbols = set()
#                 for entry in itertools.chain(symbolic_object.keys(), symbolic_object.values()):
#                     try:
#                         # entry is a sympy `Expr` and has `free_symbols` as a set
#                         symbols |= entry.free_symbols
#                     except TypeError:
#                         # rhs is a slimfit `NumExpr` and has a `free_symbols` dictionary
#                         symbols |= set(entry.free_symbols.values())
#                 return
#             elif isinstance(symbolic_object, (Expr, MatrixBase)):
#                 symbols |= symbolic_object.free_symbols
#                 # return {symbol.name: symbol for symbol in sorted(symbolic_object.free_symbols, key=str)}
#             else:
#                 raise TypeError(f"Invalid type {type(symbolic_object)!r}")

#         return {symbol.name: symbol for symbol in sorted(symbols, key=str)}


# def clear_symbols():
#     clear_cache()
#     FitSymbol._instances = {}


# class FitSymbol(Symbol):
#     _instances: dict[str, FitSymbol] = {}

#     def __new__(cls, name: str):
#         # Bypass the sympy cache
#         if name.startswith("__"):
#             raise ValueError("Double underscore leading names are limited to internal use.")
#         if name in cls._instances:
#             obj = cls._instances[name]
#         else:
#             obj = Symbol.__new__(cls, name)
#             cls._instances[name] = obj
#         return obj

#     def _sympystr(self, printer, *args, **kwargs):
#         return printer.doprint(self.name)

#     _lambdacode = _sympystr
#     _numpycode = _sympystr
#     _pythoncode = _sympystr
