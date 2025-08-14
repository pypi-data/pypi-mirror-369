import lmfit as lm
import numpy as np

from smitfit.loss import SELoss, Loss
from smitfit.model import Model
from smitfit.parameter import Parameters
from smitfit.result import Result
from smitfit.utils import flat_concat


# WIP class to replace Minimize
# this Minimize also supports scalar loss functions instead of requiring residuals
class NewMinimize:
    def __init__(
        self,
        loss: Loss,
        parameters: Parameters,
        xdata: dict[str, np.ndarray],
    ):
        self.loss = loss
        self.parameters = parameters
        self.xdata = xdata

    def fit(self, residuals=True, method: str | None = None):
        lm_params = lm.Parameters()
        for par in self.parameters:
            lm_params.add(
                par.symbol.name,
                value=par.guess,
                min=par.bounds[0],
                max=par.bounds[1],
                vary=not par.fixed,
            )

        def residual(param):
            return flat_concat(self.loss.residuals(**self.xdata, **param.valuesdict()))

        def loss(param):
            return float(self.loss(**self.xdata, **param.valuesdict()))

        minfunc = residual if residuals else loss

        if method is None and residuals:
            method = "leastsq"
        elif method is None:
            method = "lbfgsb"

        result = lm.minimize(minfunc, lm_params, method=method)
        fit_parameters = {k.name: result.params[k.name].value for k in self.parameters.free}

        # TODO redchi, aic, bic, r_squared
        gof_qualifiers = {"chisqr": result.chisqr}
        if result.errorbars:
            errors = {k.name: result.uvars[k.name].std_dev for k in self.parameters.free}
        else:
            errors = {}

        return Result(
            fit_parameters=fit_parameters,
            gof_qualifiers=gof_qualifiers,
            errors=errors,
            fixed_parameters=self.parameters.fixed.guess,
            guess=self.parameters.free.guess,
            base_result=result,
        )


class Minimize:
    def __init__(
        self,
        model: Model,
        parameters: Parameters,
        xdata: dict[str, np.ndarray],
        ydata: dict[str, np.ndarray],
    ):
        self.loss = SELoss(model, ydata)
        self.parameters = parameters
        self.xdata = xdata

    def fit(self):
        lm_params = lm.Parameters()
        for par in self.parameters:
            lm_params.add(
                par.symbol.name,
                value=par.guess,
                min=par.bounds[0],
                max=par.bounds[1],
                vary=not par.fixed,
            )

        def residual(param):
            return flat_concat(self.loss.residuals(**self.xdata, **param.valuesdict()))

        result = lm.minimize(residual, lm_params)
        fit_parameters = {k.name: result.params[k.name].value for k in self.parameters.free}

        # TODO redchi, aic, bic, r_squared
        gof_qualifiers = {"chisqr": result.chisqr}
        if result.errorbars:
            errors = {k.name: result.uvars[k.name].std_dev for k in self.parameters.free}
        else:
            errors = {}

        # fixed_parameters = {k.name: result.params[k.name].value for k in self.parameters.fixed}
        # check identical with self.parameters.fixed.guess

        return Result(
            fit_parameters=fit_parameters,
            gof_qualifiers=gof_qualifiers,
            errors=errors,
            fixed_parameters=self.parameters.fixed.guess,
            guess=self.parameters.free.guess,
            base_result=result,
        )
