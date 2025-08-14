import numpy as np
from smitfit.loss import MSELoss
from smitfit.minimize import Minimize
from smitfit.model import Model
from smitfit.symbol import Symbols


def test_fit():
    s = Symbols("x y a b")
    model = Model({s.y: s.a * s.x + s.b})  # type: ignore

    # Generate Ground-Truth data
    np.random.seed(43)
    gt = {"a": 0.15, "b": 2.5}

    xdata = np.linspace(0, 11, num=100)
    ydata = gt["a"] * xdata + gt["b"]

    noise = np.random.normal(0, scale=ydata / 10.0 + 0.2)
    ydata += noise
    parameters = model.define_parameters("a b")

    loss = MSELoss(model, dict(y=ydata))
    objective = Minimize(loss, parameters, dict(x=xdata))
    result = objective.fit()

    expected = {"a": np.array(0.14567421), "b": np.array(2.5566292)}
    for k, v in result.parameters.items():
        assert np.allclose(v, expected[k])
