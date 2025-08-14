"""
Fitting by minimzing the negative log-likelihood of a Gaussian Mixture Model (GMM) using Smitfit,
including error analysis via bootstrap and Fisher information matrix.

"""

# %%
import numpy as np
import ultraplot as uplt
from smitfit.parameter import pack, unpack
from smitfit.symbol import Symbols
import sympy as sp
from smitfit.model import Model
from smitfit.function import Function
from smitfit.loss import NLLLoss
import numdifftools as nd
from smitfit.minimize import Minimize

# %%

a = np.random.normal(loc=2.3, scale=0.4, size=1000)
b = np.random.normal(loc=1.5, scale=0.2, size=1000)

xdata = np.concatenate([a, b])
np.random.shuffle(xdata)

# %%

s = Symbols("x y mu1 mu2 sigma1 sigma2 a1 a2")


def gaussian(x, mu, sigma):
    return (1 / (sigma * sp.sqrt(2 * sp.pi))) * sp.exp(-0.5 * ((x - mu) / sigma) ** 2)


f_sym = gaussian(s.x, s.mu1, s.sigma1) * s.a1 + gaussian(s.x, s.mu2, s.sigma2) * s.a2
f_num = Function(f_sym)

gt = {"mu1": 2.3, "sigma1": 0.4, "a1": 0.5, "mu2": 1.5, "sigma2": 0.2, "a2": 0.5}
guess = {
    "mu1": 2.0,
    "sigma1": 0.2,
    "a1": 0.8,
    "mu2": 1.0,
    "sigma2": 0.1,
    "a2": 0.2,
}
x_eval = np.linspace(0.5, 4, num=1000)
y_eval = f_num(**gt, x=x_eval)
y_guess = f_num(**guess, x=x_eval)

fig, ax = uplt.subplots()
ax.hist(xdata, bins="fd", density=True, alpha=0.5, label="Data Histogram")
ax.plot(x_eval, y_eval, label="GT GMM", color="red")
ax.plot(x_eval, y_guess, label="Guess GMM", color="green")

# %%

model = Model({s.y: f_sym}).subs(s.a2, 1 - s.a1)  # enforce a1 + a2 = 1
loss = NLLLoss(model)

# %%
parameters = model.define_parameters(guess)

# %%
parameters.set_bounds({"a1": (0, 1)})
parameters.set_positive("sigma1", "sigma2")
for p in parameters:
    print(p)

# %%
result = Minimize(loss, parameters, {"x": xdata}).fit()
for k in result.parameters:
    print(k, f"{result.parameters[k]:.2f}", gt[k])

# %%
y_fit = model(**result.parameters, x=x_eval)["y"]
# %%
fig, ax = uplt.subplots()
ax.hist(xdata, bins="fd", density=True, alpha=0.5, label="Data Histogram")
ax.plot(x_eval, y_eval, label="GT GMM", color="red")
ax.plot(x_eval, y_guess, label="Guess GMM", color="green")
ax.plot(x_eval, y_fit, label="Fit GMM", color="blue")
# %%

from smitfit.lmfit import NewMinimize

result = NewMinimize(
    loss,
    parameters,
    {"x": xdata},
).fit(residuals=False)  # , method='emcee')

# %%
fit_parameter_shapes = {p.name: p.shape for p in parameters.free}


def func(x: np.ndarray):
    fit_params = unpack(x, fit_parameter_shapes)
    return loss(**fit_params, x=xdata, **parameters.fixed.guess)


x = pack(result.parameters.values())
func(x)


# %%

# calculate the inverse of the hessian with numdifftools
# we can also use hess_inv from result.base_result, if available
x = pack(result.parameters.values())
hess = nd.Hessian(func)(x)
hess_inv = np.linalg.inv(hess)
# %%

# in MLE, the covariance matrix is the inverse of the Hessian
cov_mat = hess_inv
errors_fisher = unpack(np.sqrt(np.diag(cov_mat)), fit_parameter_shapes)
errors_fisher
# %%
new_x = np.random.choice(xdata, size=len(xdata), replace=True)
# %%


def fit_func(new_xdata: np.ndarray):
    result = NewMinimize(
        loss,
        parameters,
        {"x": new_xdata},
    ).fit(residuals=False)  # , method='emcee')
    return result


# %%
n_boot = 100
parameters_out = []
for _ in range(n_boot):
    new_x = np.random.choice(xdata, size=len(xdata), replace=True)

    result = fit_func(new_x)
    parameters_out.append(pack(result.fit_parameters.values()))

param_array = np.array(parameters_out)
# %%
N_sigma = 1.0
errors_bootstrap = N_sigma * np.std(param_array, axis=0)
errors_bootstrap = unpack(errors_bootstrap, {p.name: p.shape for p in parameters})

# %%
for k in errors_bootstrap:
    print(k, f"{errors_bootstrap[k]:.4f}", f"{errors_fisher[k]:.4f}", gt[k])

# %%
