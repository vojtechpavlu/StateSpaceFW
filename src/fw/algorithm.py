""""""

from abc import ABC, abstractmethod
from typing import Iterable

from .state import State
from .state_space import StateSpace, GoalOrientedStateSpace


class Algorithm(ABC):
    """Abstract class 'Algorithm' represents the most general mutual ancestor
    of all the solvers for the state space problems.

    This non-instantiable parent has only access to the actual state space and
    the algorithm name. It also defines the abstract signature of the method
    for solving the problem itself.
    """

    def __init__(self, algo_name: str, state_space: StateSpace):
        """Initor of the class. It provides creation of the instance of
        `Algorithm`, that can solve problems in state space.

        Parameters
        ----------
        algo_name : str
            Name of the algorithm

        state_space : StateSpace
            State space to be used as an abstraction of the problem to be
            solved.
        """
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
    def solve(self):
        """Abstract method `solve` responsible for performing the actual
        algorithm run.

        The algorithm can be terminated only two ways:

            - by finding the solution
            - by finding out there is no way to get to the solution

        Raises
        ------
        SolutionSuccess
            When the solution for the problem was successfully found

        SolutionFailre
            When the solution for the problem cannot be reached by this
            algorithm
        """


class FringeBasedAlgorithm(Algorithm):
    """This abstract class of algorithms defines the general protocol for
    all the algorithms that are based on the two collections:

        - fringe - collection of states meant to be searched in future

        - closed - collection of states that are already closed (the search
                   in them was performed) and are held just to prevent
                   redundant repetition
    """

    def __init__(self, algo_name: str, state_space: StateSpace):
        """Initor of the class. It provides creation of the instance of
        `Algorithm`, that can solve problems in state space.

        Parameters
        ----------
        algo_name : str
            Name of the algorithm

        state_space : StateSpace
            State space to be used as an abstraction of the problem to be
            solved.
        """
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

    @property
    def has_any_in_fringe(self) -> bool:
        """Returns if the fringe has any state in it. If does, it return True,
        else False."""
        return len(self.fringe) > 0

    @property
    def has_any_in_closed(self) -> bool:
        """Returns if the closed has any state in it. If does, it returns True,
        else False."""
        return len(self.closed) > 0

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
        """Adds the given state on the end of the fringe."""
        self._fringe.append(state)

    def safe_add_to_fringe(self, state: State):
        """Adds the given state on the end of the fringe; iff the state is not
        there already."""
        if not self.is_in_fringe(state):
            self._fringe.append(state)

    def add_all_to_fringe(self, states: Iterable[State]):
        """Adds all the given states to the fringe, no matter if their
        equivalents are there already."""
        self._fringe.extend(states)

    def safe_add_all_to_fringe(self, states: Iterable[State]):
        """Adds all the given states to fringe safely. It means the states
        are checked if their equivalents are not there already."""
        for state in states:
            self.safe_add_to_fringe(state)

    def add_to_closed(self, state: State):
        """Adds the given state on the end of the fringe"""
        self._closed.append(state)

    def safe_add_to_closed(self, state: State):
        """Adds the given state on the end of the closed; iff the state is not
        there already."""
        if not self.is_in_closed(state):
            self._closed.append(state)

    def add_all_to_closed(self, states: Iterable[State]):
        """Adds all the given states to the closed, no matter if their
        equivalents are there already."""
        self._closed.extend(states)

    def safe_add_all_to_closed(self, states: Iterable[State]):
        """Adds all the given states to closed safely. It means the states
        are checked if their equivalents are not there already."""
        for state in states:
            self.safe_add_to_closed(state)

    @property
    @abstractmethod
    def next_from_fringe(self) -> State:
        """This abstract method defines the protocol of picking another state
        to be searched by defining the mutual signature of the functionality.

        Usual implementation of this method is returning another state from
        fringe in one of these ways:

            - first from the end (index `[-1]`)
            - first from the start (index `[0]`)
            - with (in a way) best 'value' (like the closest to the goal)
            - by random
        """


class GoalBasedAlgorithm(Algorithm):
    """This abstract class of algorithms provides ability to consider the
    goal as an important part of information when solving the problem. Usually
    is the goal state used to find out if the state is the final one or not
    and if the algorithm achieved what it had to or not.
    """

    def __init__(self, algo_name: str, state_space: GoalOrientedStateSpace):
        """Initor of the class. It provides creation of the instance of
        `Algorithm`, that can solve problems in state space.

        Parameters
        ----------
        algo_name : str
            Name of the algorithm

        state_space : GoalOrientedStateSpace
            State space to be used as an abstraction of the problem to be
            solved.
        """
        Algorithm.__init__(self, algo_name, state_space)

    @property
    def state_space(self) -> GoalOrientedStateSpace:
        """Overrides the original `state_space` property by changing the
        return value type to `GoalOrientedStateSpace`."""
        # The state space of the correct type is set by initor
        return super().state_space

    @property
    def goal_state(self) -> State:
        """This property returns the goal state from the Goal-oriented state
        space. It's just a short hand for cleaning the usage."""
        return self.state_space.goal_state

    def difference_from_goal(self, state: State) -> float:
        """This method provides easier usage by delegating the evaluation
        on the goal-oriented state space's difference evaluator.

        Parameters
        ----------
        state : State
            State for which should be the difference from the goal state
            evaluated. When the result is zero (0), the two states are
            considered as equal.

        Returns
        -------
        float
            The result of the evaluation; the quantified difference (distance)
            between the given state and the goal one.
        """
        return self.state_space.difference_from_goal(state)


class AlgorithmTermination(Exception):
    """This exception is a mutual parent for the two ways of how the algorithm
    should end, which is by successfully finding the solution or finding out
    there is no suitable way to reach the solution.

    Terminating the algorithm by exception provides ability to easily use
    various language constructions in the algorithm itself (for example the
    recursion) providing the best possible readability.

    The only con for this way of letting the higher level to know about the
    termination by using exceptions is the programmer has to catch it.
    """

    def __init__(self, message: str, algorithm: Algorithm):
        """Initor of the termination exception.

        Parameters
        ----------
        message : str
            Message to describe the way of termination

        algorithm : Algorithm
            Algorithm that just ended
        """
        Exception.__init__(self, message)
        self._algorithm = algorithm

    @property
    def algorithm(self) -> Algorithm:
        """Algorithm that just ended."""
        return self._algorithm


class SolutionSuccess(AlgorithmTermination):
    """This class defines instances of exceptions representing the successful
    way of algorithm termination. These also provides the ability to contain
    the final state - the solution."""

    def __init__(self, algorithm: Algorithm, final_state: State):
        """Initor of the successful termination exception.

        Parameters
        ----------
        algorithm : Algorithm
            Algorithm that just successfully ended

        final_state : State
            State that was found by the algorithm and considered as the
            willed solution
        """
        AlgorithmTermination.__init__(
            self, f"{algorithm.algorithm_name}: Solution found", algorithm)
        self._final_state = final_state

    @property
    def final_state(self) -> State:
        """Returns the found solution."""
        return self._final_state


class SolutionFailure(AlgorithmTermination):
    """This class defines instances of exceptions representing the unsuccessful
    way of algorithm termination.

    This way of termination usually means the algorithm got to situation where
    it cannot bypass the obstacle it run into."""

    def __init__(self, message: str, algorithm: Algorithm):
        """Initor of unsuccessful termination exception.

        Parameters
        ----------
        message : str
            Message about the unsuccessful algorithm run. Usually describes
            the reason why the algorithm cannot reach the solution or why it
            cannot continue searching for it.

        algorithm : Algorithm
            Reference to the algorithm that just ended.
        """
        AlgorithmTermination.__init__(
            self, f"{algorithm.algorithm_name}: {message}", algorithm)



