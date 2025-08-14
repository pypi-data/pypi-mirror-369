from __future__ import annotations

from typing import Callable

import numpy as np

from smitfit.result import Result
from smitfit.parameter import pack


def bootstrap(
    fit_func: Callable[[dict[str, np.ndarray]], Result],
    err: float | dict[str, float],
    ydata: dict[str, np.ndarray],
    n_boot: int = 100,
    rng=np.random.default_rng(),
) -> np.ndarray:
    parameters_out = []
    errors = err if isinstance(err, dict) else {k: err for k in ydata}
    for _ in range(n_boot):
        new_ydata = {k: v + rng.normal(0, errors[k], size=v.shape) for k, v in ydata.items()}
        result = fit_func(new_ydata)
        parameters_out.append(pack(result.fit_parameters.values()))

    return np.array(parameters_out)
