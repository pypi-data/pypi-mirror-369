from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

from smitfit.utils import clean_types


@dataclass
class Result:
    """
    Result object.
    """

    fit_parameters: dict[str, np.ndarray]
    """Fitted parameter values"""

    gof_qualifiers: dict
    """Goodness-of-fit qualifiers"""

    errors: dict[str, float | np.ndarray] = field(default_factory=dict)

    fixed_parameters: dict[str, float | np.ndarray] = field(default_factory=dict)  # Numerical dtype
    """Values of the model's fixed parameters"""

    guess: dict = field(default_factory=dict)
    """Initial guesses"""

    metadata: dict = field(default_factory=dict)
    """Additional metadata"""

    base_result: Optional[Any] = field(default=None, repr=False)
    """Source fit result object. Can be dicts of sub results"""

    def __post_init__(self) -> None:
        if "datetime" not in self.metadata:
            now = datetime.now()
            self.metadata["datetime"] = now.strftime("%Y/%m/%d %H:%M:%S")
            self.metadata["timestamp"] = int(now.timestamp())

    def __str__(self):
        if any(np.ndim(v) != 0 for v in self.fit_parameters.values()):
            raise ValueError("Cannot print fit result with array values.")

        s = ""
        # stdev = self.stdev if self.hessian is not None else None

        p_size = max(len(k) for k in self.fit_parameters)
        if self.errors:
            s += f"{'Parameter':<{p_size}} {'Value':>10} {'Stdev':>10}\n"
        else:
            s += f"{'Parameter':<{p_size}} {'Value':>10}\n"

        for k, v in self.fit_parameters.items():
            s += f"{k:<{max(p_size, 9)}} {v:>10.3g}"
            if self.errors:
                s += f" {self.errors[k]:>10.3g}"
            s += "\n"

        return s

    def to_dict(self) -> dict:
        """
        Convert the fit result to a dictionary.

        Returns:
            Dictionary representation of the fit result.
        """
        keys = [
            "gof_qualifiers",
            "fit_parameters",
            "errors",
            "fixed_parameters",
            "guess",
            "metadata",
        ]

        d = {k: v for k in keys if (v := getattr(self, k)) is not None}

        return clean_types(d)

    def to_yaml(self, path: Union[os.PathLike[str], str], sort_keys: bool = False) -> None:
        """
        Save the fit result as yaml.

        Args:
            path: Path to save to.
            sort_keys: Boolean indicating whether to sort the keys.

        """
        import yaml

        Path(path).write_text(yaml.dump(self.to_dict(), sort_keys=sort_keys))

    @property
    def parameters(self) -> dict[str, float | np.ndarray]:
        return {**self.fit_parameters, **self.fixed_parameters}
