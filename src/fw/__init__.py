"""This package defines the actual framework of the whole system. It defines
protocols of the states, state spaces and algorithms."""

# Package-initor shorthand import index
from algorithm import (
    Algorithm, FringeBasedAlgorithm, GoalBasedAlgorithm, AlgorithmTermination,
    SolutionSuccess, SolutionFailure)

from state import State, Operator, DifferenceEvaluator

from state_space import StateSpace, GoalOrientedStateSpace, StateSpaceShuffle

