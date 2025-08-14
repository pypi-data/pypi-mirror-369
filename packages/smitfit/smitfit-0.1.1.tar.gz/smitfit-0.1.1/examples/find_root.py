# %%

from smitfit.root import Root
from scipy.optimize import fsolve
import numpy as np

# %%
eqns = ["x0*cos(x1) == a1", "x1*x0 - b*x1 == a2"]
root = Root(eqns)


params = {"a1": 4.0, "a2": 5, "b": 1.0}
guess = {"x0": 1.0, "x1": 1.0}

root = Root(eqns)  # lambify once
root.set_x0(guess)
root.set_args(params)

# %%
# example at: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html#scipy.optimize.fsolve
fsolve(root.func, root.x0, root.args)
# >>> array([6.50409711, 0.90841421])

# %%
# %timeit fsolve(root.func, root.x0, root.args)
# 598 us


# %%
def func(x):
    return [x[0] * np.cos(x[1]) - 4, x[1] * x[0] - x[1] - 5]


# %%
# %timeit fsolve(root.func, root.x0, root.args)
# 30 us
# %%
