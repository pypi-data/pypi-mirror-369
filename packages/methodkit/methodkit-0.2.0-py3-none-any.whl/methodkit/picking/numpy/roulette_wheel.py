import random
from collections.abc import Sequence
from typing import Generic, TypeVar

import numpy as np

__all__ = ["NumpyRouletteWheelSelector"]


_T = TypeVar("_T")


class NumpyRouletteWheelSelector(Generic[_T]):
    """
    Roulette wheel selector using numpy.

    This is a faster implementation than the one in the base class. All the fitness values are stored in a numpy
    array, which is much faster then a Python list when computing probabilities.

    This class is only available if numpy is installed.
    """

    _candidates: list[_T]
    _fitness_values: np.ndarray

    def __init__(
        self,
        candidates: list[_T] | Sequence[_T],
        fitness_values: np.ndarray | float | None = None,
    ) -> None:
        """
        Initialize the roulette wheel selector.

        Args:
            candidates:
                The candidates to select from.
            fitness_values:
                The fitness values of the candidates.

        If fitness_values is None, all candidates will have the same fitness value equal to the length of the
        candidate list. If it's a float, all candidates will have the same fitness value equal to the float.
        Otherwise, the length of the fitness_values must be equal to the length of the candidates.
        """
        # Initialize candidates
        if isinstance(candidates, list):
            self._candidates = candidates
        else:
            self._candidates = list(candidates)

        # Initialize fitness values
        if fitness_values is None:
            self._fitness_values = np.full(len(self._candidates), len(self._candidates))
        elif isinstance(fitness_values, np.ndarray):
            self._fitness_values = fitness_values
        else:
            self._fitness_values = np.full(len(self._candidates), fitness_values)

        assert len(self._candidates) == len(self._fitness_values), (
            "candidates and fitness values must be of the same length"
        )

    def update(self, index: int, delta_fitness_value: float) -> None:
        """
        Update the fitness value of a candidate at the given index.

        Args:
            index:
                The index of the candidate to update.
            delta_fitness_value:
                The ratio of the delta to add to the fitness value. Defaults to 1.0.
        """
        self._fitness_values[index] += delta_fitness_value

    def select(self) -> _T:
        """
        Select a candidate according to the roulette wheel selection algorithm.

        Returns:
            The selected candidate.
        """
        probabilities = np.cumsum(self._fitness_values / self._fitness_values.sum())  # pyright: ignore[reportAny]
        target = random.random()
        index = np.nonzero(probabilities >= target)[0][0]  # pyright: ignore[reportAny]
        return self._candidates[index]  # pyright: ignore[reportUnknownVariableType]
