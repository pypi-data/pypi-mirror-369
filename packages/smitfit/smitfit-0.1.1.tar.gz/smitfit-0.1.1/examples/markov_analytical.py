"""
markov chain by matrix exponentiation
"""
# %%
from __future__ import annotations

import numpy as np
import sympy as sp
import ultraplot as uplt
from smitfit.loss import MSELoss
from smitfit.markov import extract_states, generate_transition_matrix
from smitfit.minimize import Minimize
from smitfit.model import Model
from smitfit.parameter import Parameters
from smitfit.symbol import symbol_matrix

# %%
np.random.seed(43)

# %%
# Ground truth parameter values for generating data and fitting
gt_values = {
    "k_A_B": 1e0,
    "k_B_A": 5e-2,
    "k_B_C": 5e-1,
    "y0_A": 1.0,
    "y0_B": 0.0,
    "y0_C": 0.0,
}

# %%
# Generate markov chain transition rate matrix from state connectivity string(s)
connectivity = ["A <-> B -> C"]
m = generate_transition_matrix(connectivity)

xt = sp.exp(m * sp.Symbol("t"))

# %%
states = extract_states(connectivity)
y0 = symbol_matrix(name="y0", shape=(3, 1), suffix=states)
# %%

model = Model({sp.Symbol("y"): xt @ y0})
model.expr[sp.Symbol("y")]
# %%

rate_params = Parameters.from_symbols(m.free_symbols)
y0_params = Parameters.from_symbols(y0.free_symbols)

parameters = rate_params + y0_params

# %%

model.expr
# %%
num = 50
xdata = {"t": np.linspace(0, 11, num=num)}

# Calling a matrix based model expands the dimensions of the matrix on the first axis to
# match the shape of input variables or parameters.
populations = model(**gt_values, **xdata)["y"]
populations.shape
# %%

ydata = {"y": populations + np.random.normal(0, 0.05, size=num * 3).reshape(populations.shape)}
ydata["y"].shape  # shape of the data is (50, 3, 1)

# %%
loss = MSELoss(model, ydata)
objective = Minimize(loss, parameters, xdata)
result = objective.fit()

# %%
# Compare fit result with ground truth parameters
for k, v in result.parameters.items():
    print(f"{k:5}: {v:10.2}, ({gt_values[k]:10.2})")

# %%
color = ["#7FACFA", "#FA654D", "#8CAD36"]
cycle = uplt.Cycle("color")

eval_data = {"t": np.linspace(0, 11, 1000)}
y_eval = model(**result.parameters, **eval_data)["y"]

# %%
fig, ax = uplt.subplots()
# currently color cycling is broken: https://github.com/Ultraplot/ultraplot/issues/25
ax.scatter(xdata["t"], ydata["y"].squeeze(), cycle=cycle)
ax.line(eval_data["t"], y_eval.squeeze(), cycle=cycle)
ax.format(xlabel="Time", ylabel="Population Fraction")
uplt.show()
# %%
