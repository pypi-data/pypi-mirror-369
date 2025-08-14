# %%
import numpy as np
import ultraplot as uplt

from smitfit.model import Model
from smitfit.symbol import Symbols
from smitfit.lmfit import Minimize

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

result = Minimize(model, parameters, xdata, ydata).fit()

result.parameters, result.errors

# %%

# compare to numpy polyfit
np.polyfit(xdata["x"], ydata["y"], deg=1)

# %%

fig, ax = uplt.subplots()
ax.scatter(xdata["x"], ydata["y"])
ax.plot(xdata["x"], model(**result.parameters, **xdata)["y"], color="r")

# %%
