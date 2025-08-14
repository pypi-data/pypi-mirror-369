# %%

import numdifftools as nd
import numpy as np
import ultraplot as uplt

from smitfit.loss import SELoss
from smitfit.minimize import Minimize
from smitfit.model import Model
from smitfit.parameter import pack, unpack
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
# lets calculate the errors by hand and compare them

# we evalulate the model at the fit parameters
ans = model(x=x_arr, **result.parameters)

# we flatten model and experimental data to compare
f = flat_concat({k: ans[k] for k in ydata})
y = flat_concat(ydata)

residuals = y - f

N = len(y)  # number of datapoints
P = len(result.parameters)  # number of parameters

# reduced chi-squared
s_squared = np.sum(residuals**2) / (N - P)

# calculate the inverse of the hessian with numdifftools
# we can also use hess_inv from result.base_result, if available
x = pack(result.parameters.values())
hess = nd.Hessian(minimize.func)(x)
hess_inv = np.linalg.inv(hess)

# the covariance matrix is now 2*s_squared * hess_inv
cov_mat = 2 * s_squared * hess_inv
std_err = np.sqrt(np.diag(cov_mat))

# unpack back as a dictionary
unpack(std_err, {p.name: p.shape for p in parameters}), result.errors

# %%
