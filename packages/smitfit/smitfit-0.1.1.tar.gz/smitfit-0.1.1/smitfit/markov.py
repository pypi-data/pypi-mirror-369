from functools import reduce
from operator import add
from typing import Type

from sympy import Matrix, Symbol, zeros

OPERATORS = ["<->", "<-", "->"]


def generate_transition_matrix(
    connectivity: list[str],
    parameter_prefix="k",
    symbol_class: Type[Symbol] = Symbol,
) -> Matrix:
    all_states = extract_states(connectivity)

    b = ["_" in s for s in all_states]
    if any(b):
        raise ValueError("Underscores are not allowed in state names")

    trs_matrix = zeros(len(all_states), len(all_states))
    for conn in connectivity:
        split = conn.split(" ")
        states = [s for s in split if s not in OPERATORS]

        for current_state in states:
            i = split.index(current_state)
            current_idx = all_states.index(current_state)

            # look to the left
            if i >= 2:
                op = split[i - 1]
                other_state = split[i - 2]  # refactor other
                other_idx = all_states.index(other_state)
                if op in ["->", "<->"]:  # flux from other state to current state
                    # elem = self.create_element(other_state, current_state)
                    elem = symbol_class(f"{parameter_prefix}_{other_state}_{current_state}")
                    trs_matrix[current_idx, other_idx] += elem

                if op in ["<-", "<->"]:  # flux from current state to other state
                    # elem = self.create_element(current_state, other_state)
                    elem = symbol_class(f"{parameter_prefix}_{current_state}_{other_state}")
                    trs_matrix[current_idx, current_idx] -= elem

            # look to the right
            if i <= len(split) - 2:
                op = split[i + 1]
                other_state = split[i + 2]
                other_idx = all_states.index(other_state)

                if op in ["<-", "<->"]:  # flux from other state to current state
                    # elem = self.create_element(other_state, current_state)
                    elem = symbol_class(f"{parameter_prefix}_{other_state}_{current_state}")
                    trs_matrix[current_idx, other_idx] += elem
                if op in ["->", "<->"]:  # flux from current state to other state
                    # elem = self.create_element(current_state, other_state)
                    elem = symbol_class(f"{parameter_prefix}_{current_state}_{other_state}")
                    trs_matrix[current_idx, current_idx] -= elem

    return trs_matrix


def extract_states(connectivity: list[str]) -> list[str]:
    """
    Args:
        connectivity: List of reaction equations.

    Returns:
        List of states found in all reaction equations.

    """

    # extract states from connectivity list
    all_states = [
        s for s in reduce(add, [eqn.split(" ") for eqn in connectivity]) if s not in OPERATORS
    ]

    # Remove duplicates, keep order
    all_states = list(dict.fromkeys(all_states))

    return all_states
