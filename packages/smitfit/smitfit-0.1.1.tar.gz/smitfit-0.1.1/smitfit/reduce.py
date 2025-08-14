from __future__ import annotations

from typing import Callable, Union

import numpy as np

ReductionStrategy = Callable[[dict[str, np.ndarray]], Union[float, np.ndarray]]


def mean_reduction(residuals: dict[str, np.ndarray]) -> float:
    size = sum(arr.size for arr in residuals.values())
    total = sum(r.sum() for r in residuals.values())
    return total / size


def sum_reduction(residuals: dict[str, np.ndarray]) -> float:
    return sum(r.sum() for r in residuals.values())


def concat_reduction(residuals: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate([a.ravel() for a in residuals.values()])
