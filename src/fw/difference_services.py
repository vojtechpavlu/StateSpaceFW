"""This module defines the most basic metrics for evaluating difference.
Its' implementation is meant to be the most abstract as possible to be used
in the widest possible range of usages.

Usually it's needed to redefine the two states the difference is about to be
quantified to be transferred in to two iterables of usable type, or better
said, transformation of the two states in two vectors is expected.

By difference is assumed to be mathematically the same as a general
distance definition:

    There is function `d: S x S -> R`, where `s ∈ S`:

        1) `∀ s1, s2 ∈ S, d(s1, s2) >= 0`
        2) `∀ s1, s2 ∈ S, d(s1, s2) = d(s2, s1)`
        3) `∀ s1, s2 ∈ S, d(s1, s2) = 0  <=>  s1 = s2`
        4) `∀ s1, s2, s3 ∈ S, d(s1, s2) + d(s2, s3) >= d(s1, s3)`
"""

from abc import ABC, abstractmethod
from typing import Iterable


class DistanceService(ABC):
    """Abstract mutual parent of the all distance evaluating services. These
    services provides quantification of the difference between two states.
    This functionality is defined by the implementation of abstract method
    'evaluate' by the descendants of this class."""

    @abstractmethod
    def evaluate(self, state1, state2) -> float:
        """This abstract method sets the most general protocol of the
        difference quantification.

        This method takes two (at this point type-unspecified) states, which
        mutual distance should be evaluated.

        The returned value is always of type 'float'."""


class HammingDistance(DistanceService):
    """Hamming distance is distance between two equally sized and ordered sets,
    where the actual difference is defined by the number of different elements.
    For example distance between words 'karolin' and 'kathrin' is equal to 3.

    Further reading at: https://en.wikipedia.org/wiki/Hamming_distance
    """

    def evaluate(self, state1: Iterable, state2: Iterable) -> float:
        """This evaluation returns the number of different elements. Both the
        items types in these iterables has to be comparable between each other.

        Parameters
        ----------
        state1: Iterable
            Any iterable of a specified length that is the same as the other
            states'

        state2: Iterable
            Any iterable of a specified length that is the same as the other
            states'
        """
        # Setting the two vectors in to tuples to get properties of sizeable
        state1 = tuple(state1)
        state2 = tuple(state2)

        # If the dimension of the two vectors is the same
        if len(state1) == len(state2):

            # When the two vectors are equal, the diff is 0 (default)
            total_difference = 0

            # For each dimension
            for index, value in enumerate(state1):

                # If the two values at the position are not equal
                if value != state2[index]:

                    # Increase the difference by one
                    total_difference += 1

            # Return the total difference between two vectors
            return total_difference

        # If the lengths are not the same
        raise Exception("Cannot compare two states of different dimensions")


class ManhattanDistance(DistanceService):
    """Manhattan distance (also known as Taxicab distance) is a sum of absolute
    differences between two vectors' coordinates.

    Further reading at: https://en.wikipedia.org/wiki/Taxicab_geometry.
    """

    def evaluate(self, state1: Iterable[float],
                 state2: Iterable[float]) -> float:
        """The difference is evaluated as a sum of differences between two
        given vectors of float numbers. Both the vectors has to be with equal
        length (dimension), otherwise it cannot be calculated.
        """
        state1 = tuple(state1)
        state2 = tuple(state2)

        # If both states are the same dimension
        if len(state1) == len(state2):
            total_difference = 0

            # For each dimension in both states
            for index, value in enumerate(state1):

                # Add the abs difference between the states in the dimension
                total_difference += abs(state2[index] - value)

            # Return sum of the absolute differences
            return total_difference

        # If the lengths are not the same
        raise Exception("Cannot compare two states of different dimensions")


class EuclideanDistance(DistanceService):
    """"""

    def evaluate(self, state1: Iterable[float],
                 state2: Iterable[float]) -> float:
        """"""
        state1 = tuple(state1)
        state2 = tuple(state2)

        if len(state1) == len(state2):
            total_difference = 0
            for index, value in enumerate(state1):

                # Make the difference in each dimension squared
                total_difference += (state2[index] - value) ** 2

            # Return root of the sum of squared differences in each dimension
            return total_difference ** 0.5

        # If the lengths are not the same
        raise Exception("Cannot compare two states of different dimensions")


