# %%

import numpy as np
import ultraplot as uplt


from smitfit.expr import CustomFunction
from smitfit.loss import SELoss
from smitfit.minimize import Minimize
from smitfit.model import Model
import sympy as sp

# %%

# Generate Ground-Truth data
np.random.seed(43)
gt = {"a": 0.15, "b": 2.5}

x_arr = np.linspace(0, 11, num=100)
y_arr = gt["a"] * x_arr + gt["b"]

noise = np.random.normal(0, scale=y_arr / 10.0 + 0.2)
y_arr += noise

xdata, ydata = {"x": x_arr}, {"y": y_arr}


def func(**kwargs):
    return kwargs["a"] * kwargs["x"] + kwargs["b"]


custom_func = CustomFunction(func, sp.symbols("a x b"))

# %%
model = Model({sp.Symbol("y"): custom_func})
parameters = model.define_parameters("a b")

# %%
loss = SELoss(model, ydata)
minimize = Minimize(loss, parameters, xdata)
result = minimize.fit()
result.parameters
# %%

fig, ax = uplt.subplots()
ax.scatter(xdata["x"], ydata["y"])
ax.plot(xdata["x"], model(**result.parameters, **xdata)["y"], color="r")

# %%
