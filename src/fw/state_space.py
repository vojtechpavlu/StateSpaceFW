"""This module contains the actual state space abstraction definition."""


from typing import Iterable
from abc import ABC
from random import choice

from .state import State, Operator, DifferenceEvaluator


class StateSpace(ABC):
    """This abstract class is the most general mutual ancestor of all the
    state spaces. It provides only the most basic functionality to define
    the problem."""

    def __init__(self, initial_state: State, operators: Iterable[Operator],
                 diff_evaluator: DifferenceEvaluator):
        """Initor of the abstract class.

        Parameters
        ----------
        initial_state : State
            State the `Algorithm` instance should start from when seeking for
            the solution.

        operators: Iterable of Operator
            Iterable collection of all applicable operators in the problem
            solving.

        diff_evaluator : DifferenceEvaluator
            Evaluator used to quantify the difference between two states. If
            the difference is equal to zero (0), the system considers these
            two as equivalent.
        """
        self._initial_state = initial_state
        self._operators = tuple(operators)
        self._diff_evaluator = diff_evaluator

    @property
    def initial_state(self) -> State:
        """State the solution search starts in."""
        return self._initial_state

    @property
    def operators(self) -> tuple[Operator]:
        """Tuple of operators that can be used while searching for the
        solution. Not all of these may be used on every state in the
        state space!"""
        return self._operators

    @property
    def difference_evaluator(self) -> "DifferenceEvaluator":
        """Evaluator used for calculation of the difference between two states.
        """
        return self._diff_evaluator

    @difference_evaluator.setter
    def difference_evaluator(self, diff_evaluator: "DifferenceEvaluator"):
        """Setter for the evaluator used for calculation of the difference
        between two states."""
        self._diff_evaluator = diff_evaluator

    def difference(self, state1: State, state2: State) -> float:
        """Method defining the signature of the states difference evaluation.

        The calculated difference is representing inverse likelihood of two
        states in decimal (float) value. This evaluation is done using a given
        difference evaluator.
        """
        return self.difference_evaluator.evaluate_difference(state1, state2)

    def difference_from_initial(self, state: State) -> float:
        """Returns the evaluation between the initial state and the given
        state."""
        return self.difference(self.initial_state, state)


class GoalOrientedStateSpace(StateSpace):
    """This type of state space is constructed as Goal-oriented, which means
    the willed result is a specific sequence of operators leading to the
    state or it's equivalent."""

    def __init__(self, initial_state: State, operators: Iterable[Operator],
                 diff_evaluator: DifferenceEvaluator, goal_state: State):
        """Initor of the abstract class.

        Parameters
        ----------
        initial_state : State
            State the `Algorithm` instance should start from when seeking for
            the solution.

        operators: Iterable of Operator
            Iterable collection of all applicable operators in the problem
            solving.

        diff_evaluator : DifferenceEvaluator
            Evaluator used to quantify the difference between two states. If
            the difference is equal to zero (0), the system considers these
            two as equivalent.

        goal_state : State
            State (or it's equivalent) which the algorithm crawling over the
            state space should find.
        """
        StateSpace.__init__(self, initial_state, operators, diff_evaluator)
        self._goal_state = goal_state

    @property
    def goal_state(self) -> State:
        """Returns the state which should be found."""
        return self._goal_state

    @property
    def init_goal_equality(self) -> bool:
        """Returns if the initial and the goal state are equivalent. If their
        mutual distance (difference) is equal to zero (0), it returns True,
        else it returns False."""
        return self.difference_evaluator.are_the_same(
            self.initial_state, self.goal_state)

    def difference_from_goal(self, state: State) -> float:
        """"""
        return self.difference(state, self.goal_state)


class StateSpaceShuffle:
    """Instances of this class provides the random shuffle of the state space.
    This is done by randomly applying given operators given number of times.
    The given 'initial' state is actually the goal state from which the random
    operator application begins; the result state (after the sequence of the
    operators) is the actual initial state.

    Because the goal (canonical, ordered or in any other way the final state)
    is given, the produced state space is always meant to be the goal oriented.

    Instances of this class are meant to be used mostly for testing purposes.
    """

    def __init__(self, goal_state: State, operators: Iterable[Operator],
                 diff_evaluator: DifferenceEvaluator, shuffle_grade: int):
        """Initor of the class.

        Parameters
        ----------
        goal_state : State
            The state, where the shuffle should start from. On this state are
            the randomly picked operators applied, which produces an actual
            initial state after a given number of iterations.

        operators : Iterable of Operator
            Iterable collection of operators that can be applied on a state of
            the produced state space.

        diff_evaluator : DifferenceEvaluator
            Evaluator of two states used to quantify the difference between
            them.

        shuffle_grade : int
            The number of iterations of picking and applying the operator on
            the state. This defines the grade of randomization.
        """

        self._goal_state = goal_state
        self._operators = tuple(operators)
        self._diff_evaluator = diff_evaluator
        self._shuffle_grade = shuffle_grade

        # Shuffle grade check
        if self._shuffle_grade < 0:
            raise Exception(
                f"Shuffle grade cannot be negative number: {shuffle_grade}")

    @property
    def shuffle_grade(self) -> int:
        """Returns the number of iterations of picking and applying the
        operator on the state."""
        return self._shuffle_grade

    @property
    def goal_state(self) -> State:
        """Returns the former initial state (before the randomization), future
        goal state the algorithm should get to."""
        return self._goal_state

    @property
    def operators(self) -> tuple[Operator]:
        """Tuple of operators that can be used in this state space."""
        return self._operators

    @property
    def diff_evaluator(self) -> DifferenceEvaluator:
        """Evaluator used to measure the difference between two states."""
        return self._diff_evaluator

    def shuffle(self) -> StateSpace:
        """The procedure of randomizing the state space initial state.
        This method sets the goal state as the initial, applies random
        operators on the state (and it's descendants) by the given times
        and builds the initial state from the goal.
        """
        # The current state space the randomization starts from is the goal
        current_state = self.goal_state

        # Randomize in number of iterations
        for _ in range(self.shuffle_grade):

            # Selection of the applicable operators only
            applicable_ops = current_state.filter_applicable(self.operators)

            # Applying one randomly picked on the current state to produce
            # another one, which is set to be the current one
            current_state = current_state.apply(choice(applicable_ops))

        # Clear the future initial state from previous paths
        current_state.parent_state = None
        current_state.applied_operator = None

        # Return the newly created state space
        return GoalOrientedStateSpace(current_state, self.operators,
                                      self.diff_evaluator, self.goal_state)




