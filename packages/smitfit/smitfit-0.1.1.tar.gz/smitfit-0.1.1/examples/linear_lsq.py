# %%

import numpy as np
import ultraplot as uplt

from smitfit.loss import SELoss
from smitfit.minimize import Minimize
from smitfit.model import Model
from smitfit.symbol import Symbols

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

# %%
loss = SELoss(model, ydata)
minimize = Minimize(loss, parameters, xdata)
parameters["a"].set_bounds(0.3, None)

result = minimize.fit()
result.parameters

# %%

parameters["a"].set_bounds(0.3, None)
minimize = Minimize(loss, parameters, xdata)
self = minimize

lb, ub = [], []
for p in self.parameters.free:
    size = np.prod(p.shape, dtype=int)
    lb += [p.bounds[0]] * size
    ub += [p.bounds[1]] * size

if all(elem is None for elem in lb + ub):
    print("all none")
else:
    # replace none in lb with -np.inf
    lb = [-np.inf if elem is None else elem for elem in lb]
    ub = [np.inf if elem is None else elem for elem in ub]

lb, ub
from scipy.optimize import Bounds

bounds = Bounds(lb, ub)  # type: ignore
bounds
# %%
# %%
# compare to numpy polyfit
np.polyfit(xdata["x"], ydata["y"], deg=1)

# %%

fig, ax = uplt.subplots()
ax.scatter(xdata["x"], ydata["y"])
ax.plot(xdata["x"], model(**result.parameters, **xdata)["y"], color="r")

# %%
