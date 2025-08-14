from typing import Optional

from smitfit.model import Model
from smitfit.reduce import mean_reduction, sum_reduction

import numpy as np


class Loss:
    """sum/average reduction"""

    def __call__(self, **kwargs) -> float:
        return 0.0


class SELoss(Loss):
    """sum of squared errors"""

    # todo super call pass model
    def __init__(self, model: Model, y_data: dict, weights: Optional[dict] = None):
        self.model = model
        self.y_data = y_data
        self.weights = weights or {}

    def residuals(self, **kwargs):
        y_model = self.model(**kwargs)

        return {k: y_model[k] - self.y_data[k] for k in self.y_data.keys()}

    def squares(self, **kwargs):
        y_model = self.model(**kwargs)

        squares = {
            k: ((y_model[k] - self.y_data[k]) * self.weights.get(k, 1)) ** 2
            for k in self.y_data.keys()
        }

        return squares

    def __call__(self, **kwargs) -> float:
        squares = self.squares(**kwargs)

        return sum_reduction(squares)


class MSELoss(SELoss):
    def __call__(self, **kwargs) -> float:
        squares = self.squares(**kwargs)

        return mean_reduction(squares)


class NLLLoss(Loss):
    """Negative Log Likelihood Loss"""

    def __init__(self, model: Model, weights: Optional[dict] = None):
        self.model = model
        self.weights = weights or {}

    def __call__(self, **kwargs) -> float:
        y_model = self.model(**kwargs)

        log_likelihoods = {k: -self.weights.get(k, 1) * np.log(y_model[k]) for k in y_model}
        return sum_reduction(log_likelihoods)
