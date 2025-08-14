# %%

"""
estimating erros by bootstrapping
https://stackoverflow.com/questions/14581358/getting-standard-errors-on-fitted-parameters-using-the-optimize-leastsq-method-i

See also
Efron, B. & Tibshirani, R. An Introduction to the Bootstrap (Chapman & Hall, 1993).

"""

# %%

import numpy as np

from smitfit.error import bootstrap
from smitfit.loss import SELoss
from smitfit.minimize import Minimize
from smitfit.model import Model
from smitfit.parameter import unpack
from smitfit.symbol import Symbols
from smitfit.utils import flat_concat

# %%

s = Symbols("x y a b")
model = Model({s.y: s.a * s.x + s.b})  # type: ignore

# Generate Ground-Truth data
np.random.seed(43)
gt = {"a": 0.15, "b": 2.5}

x_arr = np.linspace(0, 11, num=100)
y_arr = gt["a"] * x_arr + gt["b"]

noise = np.random.normal(0, scale=y_arr / 10.0 + 0.2)
y_arr += noise

xdata, ydata = {"x": x_arr}, {"y": y_arr}

# %%
parameters = model.define_parameters("a b")
loss = SELoss(model, ydata)
minimize = Minimize(loss, parameters, xdata)
result = minimize.fit()

# %%

y_err = 0.0  # additional systematic error
residuals = flat_concat(loss.residuals(**result.parameters, **xdata))
residual_std = np.std(residuals)
total_error = np.sqrt(residual_std**2 + y_err**2)

# %%


def do_fit(new_ydata):
    loss = SELoss(model, new_ydata)
    minimize = Minimize(loss, parameters=parameters, xdata=xdata)
    new_result = minimize.fit()
    return new_result


param_array = bootstrap(
    do_fit,
    err=total_error,
    ydata=ydata,
)

N_sigma = 1.0
errors = N_sigma * np.std(param_array, axis=0)
errors = unpack(errors, {p.name: p.shape for p in parameters})
print(errors)

# %%

print("fit result errors")
print(result.errors)
