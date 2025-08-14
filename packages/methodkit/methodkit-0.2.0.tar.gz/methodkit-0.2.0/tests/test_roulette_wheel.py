"""
Test whether the roulette wheel works correctly.

In order to study the results' distribution, we do not update the fitness values, and the chosen ones should conform to
the uniform distribution. We use scipy to verify that.
"""

from collections import Counter
from collections.abc import Sequence

from scipy.stats import chisquare  # pyright: ignore[reportUnknownVariableType]

from methodkit.picking import RouletteWheelSelector
from methodkit.picking.numpy import NumpyRouletteWheelSelector

# random chosen parameters
_CANDIDATE_COUNT = 5
_SELECT_TIMES = 10000


def test_roulette_wheel() -> None:
    selector = RouletteWheelSelector([i for i in range(_CANDIDATE_COUNT)])
    values: list[int] = []
    for _ in range(_SELECT_TIMES):
        values.append(selector.select())
    assert _is_uniform_distribution(values), "the chosen values are not uniformly distributed"


def test_numpy_roulette_wheel() -> None:
    selector = NumpyRouletteWheelSelector([i for i in range(_CANDIDATE_COUNT)])
    values: list[int] = []
    for _ in range(_SELECT_TIMES):
        values.append(selector.select())
    assert _is_uniform_distribution(values), "the chosen values are not uniformly distributed"


def _is_uniform_distribution(values: Sequence[int]) -> bool:
    """
    Tests whether the given values are uniformly distributed.

    Args:
        values: The values to test.
    """
    observation = list(Counter(values).values())
    expectation = [len(values) / len(observation)] * len(observation)
    result = chisquare(observation, expectation)
    return result.pvalue.item() > 0.05
