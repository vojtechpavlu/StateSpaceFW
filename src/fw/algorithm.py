""""""

from abc import ABC, abstractmethod
from typing import Iterable
from random import choice

from .state import State
from .state_space import StateSpace, GoalOrientedStateSpace


class Algorithm(ABC):
    """Abstract class 'Algorithm' represents the most general mutual ancestor
    of all the solvers for the state space problems.

    This non-instantiable parent has only access to the actual state space and
    the algorithm name. It also defines the abstract signature of the method
    for solving the problem itself."""

    def __init__(self, algo_name: str, state_space: StateSpace):
        """"""
        self._algo_name = algo_name
        self._state_space = state_space

    @property
    def algorithm_name(self) -> str:
        """Specified name of the algorithm."""
        return self._algo_name

    @property
    def state_space(self) -> StateSpace:
        """State space in which the solution has to be found."""
        return self._state_space

    @abstractmethod
    def solve(self) -> State:
        """"""


class FringeBasedAlgorithm(Algorithm):
    """"""

    def __init__(self, algo_name: str, state_space: StateSpace):
        """"""
        Algorithm.__init__(self, algo_name, state_space)
        self._fringe: list[State] = [state_space.initial_state]
        self._closed: list[State] = []

    @property
    def fringe(self) -> tuple[State]:
        """'Fringe' is list of states that are about to be searched for paths
        to the desired state.

        This property returns these states contained in a tuple collection."""
        return tuple(self._fringe)

    @property
    def closed(self) -> tuple[State]:
        """'Closed' is list of states, to which all possible operators were
        already applied and further searching in them cannot contribute to
        the solution anymore.

        This property returns these states contained in a tuple collection."""
        return tuple(self._closed)

    def is_in_fringe(self, state: State) -> bool:
        """Method returning if the given state (or it's equivalent with zero
        difference) is already contained in the fringe."""
        return self._is_in(state, self.fringe)

    def is_in_closed(self, state: State) -> bool:
        """Method returning if the given state (or it's equivalent with zero
        difference) is already contained in the list of closed states."""
        return self._is_in(state, self.closed)

    def _is_in(self, state: State, container: Iterable[State]) -> bool:
        """Private method responsible for search in the given container for
        a state with zero difference from the given state.

        If there is such a state, it means the two states are equal in means
        of state space abstraction, therefore the state is contained.
        """
        # For each state in the given container of states
        for s in container:

            # If the difference between the states is equal to zero
            if self.state_space.difference_evaluator.are_the_same(s, state):
                return True

        # If none of the states has zero difference
        return False

    def add_to_fringe(self, state: State):
        """"""
        self._fringe.append(state)

    def add_to_closed(self, state: State):
        """"""
        self._closed.append(state)

    def safe_add_to_fringe(self, state: State):
        """"""
        if not self.is_in_fringe(state):
            self._fringe.append(state)

    def safe_add_to_closed(self, state: State):
        """"""
        if not self.is_in_closed(state):
            self._closed.append(state)

    @abstractmethod
    def next_from_fringe(self) -> State:
        """"""


class SolutionSuccess(Exception):
    """"""

    def __init__(self, algorithm: Algorithm, final_state: State):
        """"""
        Exception.__init__(
            self, f"{algorithm.algorithm_name}: Solution found")
        self._algorithm = algorithm
        self._final_state = final_state

    @property
    def algorithm(self) -> Algorithm:
        return self._algorithm

    @property
    def final_state(self) -> State:
        return self._final_state


class SolutionFailure(Exception):
    """"""

    def __init__(self, message: str, algorithm: Algorithm):
        """"""
        Exception.__init__(self, f"{algorithm.algorithm_name}: {message}")
        self._algorithm = algorithm

    @property
    def algorithm(self) -> Algorithm:
        return self._algorithm


class RandomOperatorPicker(Algorithm):

    def __init__(self, state_space: GoalOrientedStateSpace):
        Algorithm.__init__(self, "RandomOperatorPicker", state_space)

    @property
    def state_space(self) -> GoalOrientedStateSpace:
        return super().state_space

    def solve(self) -> State:

        # All operators available
        ops = self.state_space.operators

        # Current state the space is in
        current_state = self.state_space.initial_state

        # While there is difference between the current state and the goal
        while not self.state_space.difference_from_goal(current_state):

            # Randomly pick available operator
            applying = choice(current_state.filter_applicable(ops))

            # Apply this operator to current state and save the result
            current_state = current_state.apply(applying)

            # Notify about the action
            print(applying, "=>", current_state)

        # If the difference is zero
        return current_state


