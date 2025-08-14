import numpy as np
import pytest
import sympy as sp

from smitfit.expr import Expr, SympyExpr, SympyMatrixExpr, GetItem, CustomFunction
from smitfit.model import Model
from smitfit.composite_expr import CompositeExpr, MarkovIVP
from smitfit.operator import Add, Mul
from smitfit.symbol import symbol_matrix


class TestBasicSubstitution:
    """Test basic substitution functionality across various expression types"""

    def test_sympy_expr_subs(self):
        # Test for SympyExpr
        a, b, c, x = sp.symbols("a b c x")
        expr = SympyExpr(a * x + b)

        # Test substitution with different input formats
        # Dictionary substitution
        result1 = expr.subs({a: 2, b: 3})
        assert result1._expr == 2 * x + 3

        # List of pairs substitution
        result2 = expr.subs([(a, 2), (b, 3)])
        assert result2._expr == 2 * x + 3

        # Direct pair substitution
        result3 = expr.subs(a, c)
        assert result3._expr == c * x + b

        # Keyword arguments substitution
        result4 = expr.subs(a=5, b=6)
        assert result4._expr == 5 * x + 6

        # Mixed substitution
        result5 = expr.subs({a: 2}, b=3)
        assert result5._expr == 2 * x + 3

        # Substituting a symbol not in the expression
        result6 = expr.subs(c=10)
        assert result6._expr == a * x + b  # should be unchanged

        # Evaluation after substitution
        result7 = expr.subs(a=2, b=3)
        assert result7(x=4) == 11  # 2*4 + 3 = 11

    def test_matrix_expr_subs(self):
        # Test for SympyMatrixExpr
        a, b = sp.symbols("a b")
        matrix = sp.Matrix([[a, b], [b, a]])
        expr = SympyMatrixExpr(matrix)

        # Dictionary substitution
        result1 = expr.subs({a: 2, b: 3})
        assert result1._expr == sp.Matrix([[2, 3], [3, 2]])

        # Evaluation after substitution
        result = expr.subs(a=1, b=2)
        np.testing.assert_array_equal(result(), np.array([[1, 2], [2, 1]]))

    def test_getitem_subs(self):
        # Test for GetItem
        a, b = sp.symbols("a b")
        expr = SympyExpr(sp.Matrix([[a, b], [b, a]]))
        getitem_expr = expr[0, 1]  # Should be 'b', but since its lazy still accepts a
        assert getitem_expr.symbols == {a, b}
        assert getitem_expr(a=3, b=2) == 2

        # Test substitution propagates through GetItem
        result = getitem_expr.subs(b=5)
        assert result(a=0) == 5

        # Test the GetItem operation is preserved
        assert isinstance(result, GetItem)

    def test_composite_expr_subs(self):
        # Test for CompositeExpr
        a, b, t = sp.symbols("a b t")
        composite = CompositeExpr({"t": SympyExpr(t), "func": SympyExpr(a * t + b)})

        # Test substitution in all components
        result = composite.subs(a=2, b=3)
        assert result._expr["func"]._expr == 2 * t + 3
        assert result._expr["t"]._expr == t

        # Test evaluation after substitution
        values = result(t=5)
        assert values["func"] == 13  # 2*5 + 3 = 13

    def test_markov_ivp_subs(self):
        # Test for MarkovIVP
        t = sp.Symbol("t")
        k_ab, k_ba = sp.symbols("k_ab k_ba")

        # Simple 2-state Markov model
        trs_matrix = sp.Matrix([[-k_ab, k_ba], [k_ab, -k_ba]])
        y0 = sp.Matrix([1, 0])

        markov = MarkovIVP(t, trs_matrix, y0, domain=(0, 10))

        # Test substitution preserves all attributes
        result = markov.subs(k_ab=0.5, k_ba=0.1)

        # Check the matrix was substituted correctly
        assert result._expr["trs_matrix"]._expr == sp.Matrix([[-0.5, 0.1], [0.5, -0.1]])

        # Check that non-expr attributes are preserved
        assert result.domain == (0, 10)  # type: ignore
        assert result.ivp_defaults == {"method": "Radau"}  # type: ignore

    def test_model_subs(self):
        # Test for Model
        a, b, x, y = sp.symbols("a b x y")
        model = Model({y: a * x + b})

        # Test substitution
        result = model.subs(a=2, b=3)
        assert result.model[y] == 2 * x + 3

        # Test x_symbols are updated
        assert result.x_symbols == {x}  # 'a' and 'b' are substituted with constants

        # Test y_symbols remain unchanged
        assert result.y_symbols == {y}

        # Test evaluation
        assert result(x=4)[y.name] == 11  # 2*4 + 3 = 11

        # Test substitution with expressions
        c = sp.Symbol("c")
        result2 = model.subs(a=c**2, b=c + 1)  # type: ignore
        assert result2.model[y] == c**2 * x + c + 1
        assert result2.x_symbols == {x, c}


class TestAdvancedSubstitution:
    """Test more advanced substitution scenarios"""

    def test_chained_substitution(self):
        # Test chained substitutions
        a, b, c, d, x = sp.symbols("a b c d x")
        expr = SympyExpr(a * x + b)

        # First substitution
        result1 = expr.subs(a=c + d, b=c - d)
        # Second substitution
        result2 = result1.subs(c=2, d=1)

        assert result2._expr == 3 * x + 1  # (c+d)*x + (c-d) = (2+1)*x + (2-1) = 3*x + 1
        assert result2(x=2) == 7  # 3*2 + 1 = 7

    def test_operator_substitution(self):
        # Test substitution in operator expressions
        a, b, c, x = sp.symbols("a b c x")

        add_expr = Add(SympyExpr(a * x), SympyExpr(b))
        result1 = add_expr.subs(a=2, b=3)
        assert result1(x=4) == 11  # 2*4 + 3 = 11

        # Test with multiplication
        mul_expr = Mul(SympyExpr(a), SympyExpr(b + x))
        result2 = mul_expr.subs(a=2, b=3)
        assert result2(x=4) == 14  # 2*(3+4) = 14

    def test_substitution_with_matrices(self):
        # Test substitution with matrix expressions
        a, b = sp.symbols("a b")
        matrix1 = symbol_matrix("m", (2, 2))
        matrix2 = sp.Matrix([[a, b], [b, a]])

        # Create a model with matrix expressions
        model = Model({sp.Symbol("y"): matrix1 * matrix2})

        c, d = sp.symbols("c d")
        new_matrix = sp.Matrix([[c, d], [d, c]])
        result = model.subs([(a, c), (b, d)])

        # Check the substitution was correct
        expected_result = matrix1 * new_matrix
        assert sp.Equality(result.model[sp.Symbol("y")], expected_result)

    def test_custom_function_subs(self):
        # Test substitution in CustomFunction
        a, b = sp.symbols("a b")

        # Define a simple custom function
        def simple_func(**kwargs):
            return kwargs["a"] * 2 + kwargs["b"]

        custom = CustomFunction(simple_func, symbols=[a, b])

        # Test substitution of symbols
        c = sp.Symbol("c")
        result = custom.subs(a=c, b=5)

        # Check that symbols are unaffected
        assert result.symbols == {a, b}

        # Check that the function itself is preserved
        assert result.func == simple_func


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_substitution(self):
        # Test substitution with empty inputs
        a, x = sp.symbols("a x")
        expr = SympyExpr(a * x)

        # Empty dict
        result1 = expr.subs({})
        assert result1._expr == a * x

        # No args or kwargs
        result2 = expr.subs()
        assert result2._expr == a * x

    def test_substitution_with_numeric_values(self):
        # Test substitution with various numeric types
        a, b, x = sp.symbols("a b x")
        expr = SympyExpr(a * x + b)

        # Integer
        result1 = expr.subs(a=2, b=3)
        assert result1(x=4) == 11

        # Float
        result2 = expr.subs(a=2.5, b=3.5)
        assert result2(x=2) == 8.5  # 2.5*2 + 3.5 = 8.5

        # NumPy scalar
        result3 = expr.subs(a=np.float64(2.0), b=np.int64(3))
        assert result3(x=4) == 11.0

    def test_substitution_in_model_string_initialization(self):
        # Test substitution in a model initialized from string
        model = Model("y == a*x + b")

        # Test substitution
        result = model.subs(a=2, b=3)

        # Check that the substitution was correct
        assert result(x=4)["y"] == 11  # 2*4 + 3 = 11


if __name__ == "__main__":
    pytest.main(["-v", "tests/test_subs.py"])
