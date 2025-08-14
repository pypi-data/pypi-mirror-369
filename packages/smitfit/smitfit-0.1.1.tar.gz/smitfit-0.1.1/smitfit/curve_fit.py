from smitfit.result import Result
from smitfit.function import Function
from smitfit.parameter import Parameters, pack, unpack, scipy_bounds
import numpy as np
from scipy.optimize import curve_fit


class CurveFit:
    def __init__(self, func: Function, parameters: Parameters, xdata: dict, ydata: dict):
        self.func = func
        self.parameters = parameters
        self.xdata = xdata
        self.ydata = ydata

    def f(self, xdata: np.ndarray, *args):
        unstacked_x = {k: v for k, v in zip(self.xdata, np.atleast_2d(xdata))}
        kwargs = unpack(args, self.parameters.free.shapes)
        return self.func(**unstacked_x, **kwargs, **self.parameters.fixed.guess)

    def fit(self) -> Result:
        p0 = pack(self.parameters.free.guess.values())
        ydata = self.ydata[self.func.y.name]
        xdata = np.stack(list(self.xdata.values()))

        bounds = scipy_bounds(self.parameters.free) or (-np.inf, np.inf)
        popt, pcov, infodict, mesg, ier = curve_fit(
            self.f, xdata, ydata, p0=p0, bounds=bounds, full_output=True
        )
        base_result = dict(popt=popt, pcov=pcov, infodict=infodict, mesg=mesg, ier=ier)

        errors = unpack(np.sqrt(np.diag(pcov)), self.parameters.free.shapes)
        parameters = unpack(popt, self.parameters.free.shapes)

        f = self.func(**self.xdata, **parameters, **self.parameters.fixed.guess)
        y = self.ydata[self.func.y.name]

        gof_qualifiers = {}
        gof_qualifiers["r_squared"] = 1 - np.sum((y - f) ** 2) / np.sum((y - np.mean(y)) ** 2)
        residuals = infodict["fvec"]
        gof_qualifiers["loss"] = np.sum(residuals**2)
        gof_qualifiers["rmse"] = np.sqrt(np.mean(residuals**2))

        result = Result(
            fit_parameters=parameters,
            gof_qualifiers=gof_qualifiers,
            errors=errors,  # type: ignore
            fixed_parameters=self.parameters.fixed.guess,
            guess=self.parameters.guess,
            base_result=base_result,
        )
        return result

    def get_bounds(self) -> list[tuple[float | None, float | None]] | None:
        bounds = []
        for p in self.parameters.free:
            size = np.prod(p.shape, dtype=int)
            bounds += [p.bounds] * size

        if all((None, None) == b for b in bounds):
            return None
        else:
            return bounds
