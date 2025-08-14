"""
uses scipy.optimize.curve_fit
"""

# %%
from smitfit import Function, SELoss, Model, CurveFit
import ultraplot as uplt
import numpy as np

from smitfit.minimize import Minimize

# %%

# Generate Ground-Truth data
np.random.seed(43)
gt = {"a": 3.15, "b": 2.5, "c": 5}

x1_arr = np.linspace(0, 11, num=100)
x2_arr = np.linspace(5, 15, num=100)
y_arr = gt["a"] * x1_arr + gt["b"] + gt["c"] * np.sin(x2_arr)

noise = np.random.normal(0, scale=np.abs(y_arr / 10.0 + 0.2))
y_arr += noise
xdata, ydata = {"x1": x1_arr, "x2": x2_arr}, {"y": y_arr}

f = Function("a*x1 + b + c*sin(x2)")

# %%
parameters = f.define_parameters("a b c")
curve_fit = CurveFit(
    f,
    parameters,
    xdata,
    ydata,
)
result = curve_fit.fit()
result.parameters

# %%

# plot data and fit
fig, ax = uplt.subplots()
ax.scatter(xdata["x1"], ydata["y"], label="data")
ax.plot(xdata["x1"], f(**xdata, **result.parameters), label="fit", color="r")
ax.format(xlim=(0, 11), xlabel="x1", ylabel="y")

sub_ax = ax.twiny(xloc=("axes", -0.2), xcolor="black", xlabel="offset twin")
sub_ax.format(xlim=(5, 15), xlabel="x2", xticks=uplt.arange(5, 15, 2))


# %%

model = Model("y==a*x1 + b + c*sin(x2)")
parameters = model.define_parameters("a b c")
loss = SELoss(model, ydata)
objective = Minimize(loss, parameters, xdata)
minimize_result = objective.fit()
minimize_result.parameters

# %%

# compare the two results
print("Fit parameters:")
for k, v in result.parameters.items():
    print(f"{k}: {v:.3f} vs {minimize_result.parameters[k]:.3f}")

print("\nErrors:")
# compare the errors on the results:
for k, v in result.errors.items():
    print(f"{k}: {v:.3f} vs {minimize_result.errors[k]:.3f}")

# %%
