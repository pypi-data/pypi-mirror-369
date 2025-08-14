"""
Example demonstrating the use of symbol substitution in models.

This example shows how to create parameterized models where
some parameters are defined in terms of other parameters.
"""

# %%
import numpy as np
import sympy as sp

from smitfit.model import Model
from smitfit.minimize import Minimize
from smitfit.loss import MSELoss
import ultraplot as uplt

# %%

# Create a base model with three parameters
base_model = Model("y == a*exp(-b*x)+c")

# %%
# Generate some synthetic data
x = np.linspace(0, 10, 50)
true_values = {"a": 5.0, "b": 0.25, "c": 1.0}
y_true = true_values["a"] * np.exp(-true_values["b"] * x) + true_values["c"]
y = y_true + np.random.normal(0, 0.2, size=len(x))
xdata, ydata = {"x": x}, {"y": y}

fig, ax = uplt.subplots(refaspect=1.618)
# Plot the data
ax.scatter(x, y, label="Data")
ax.plot(x, y_true, "r-", label="True function")
ax.format(xlabel="x", ylabel="y", title="Data and True Function")

# %%
base_params = base_model.define_parameters("a, b, c")
base_loss = MSELoss(base_model, ydata)
base_objective = Minimize(base_loss, base_params, xdata)
base_result = base_objective.fit()

print("Base model fit:")
print(base_result.parameters)
print(f"Loss: {base_result.gof_qualifiers['loss']:.6f}")

# %%
# Now create a constrained model where b = a/10
# This is done by substituting b with a/10
constrained_model = base_model.subs(b=sp.Symbol("a") / 10)  # type: ignore

# Define the model's parameters - only have 'a' and 'c' now
constrained_params = constrained_model.define_parameters("a, c")
print("Constrained model parameters:", [p.symbol.name for p in constrained_params])


# %%
# Fit the constrained model
constrained_loss = MSELoss(constrained_model, ydata)
constrained_objective = Minimize(constrained_loss, constrained_params, xdata)
constrained_result = constrained_objective.fit()

print("Contrained model fit:")
print(constrained_result.parameters)
print(f"Loss: {base_result.gof_qualifiers['loss']:.6f}")

# %%

# Plot the results
fig, ax = uplt.subplots(refaspect=1.618)
ax.scatter(x, y, label="Data", color="k", alpha=0.55, markeredgecolor="none")
ax.plot(x, y_true, "r-", label="True")

# Plot base model fit
base_fit = base_model(**base_result.parameters, **xdata)["y"]
ax.plot(x, base_fit, "g--", label="Base ")

constrained_fit = constrained_model(**constrained_result.parameters, **xdata)["y"]
ax.plot(x, constrained_fit, "b-.", label="Constrained")
ax.format(xlabel="x", ylabel="y", title="Model Comparison")
ax.legend(loc="r", ncols=1)
