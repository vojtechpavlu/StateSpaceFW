""""""


from typing import Iterable
from abc import ABC, abstractmethod
from random import choice

from .state import State, Operator, DifferenceEvaluator


class StateSpace(ABC):
    """"""

    def __init__(self, initial_state: State, operators: Iterable[Operator],
                 diff_evaluator: DifferenceEvaluator):
        """"""
        self._initial_state = initial_state
        self._operators = tuple(operators)
        self._diff_evaluator = diff_evaluator

    @property
    def initial_state(self) -> State:
        """"""
        return self._initial_state

    @property
    def operators(self) -> tuple[Operator]:
        """"""
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
        """Abstract method defining the signature of the states difference
        evaluation.

        The calculated difference is representing inverse likelihood of two
        states in decimal (float) value. This evaluation is done using a given
        difference evaluator.
        """
        return self.difference_evaluator.evaluate_difference(state1, state2)

    def difference_from_initial(self, state: State) -> float:
        """"""
        return self.difference(self.initial_state, state)


class GoalOrientedStateSpace(StateSpace):
    """"""

    def __init__(self, initial_state: State, operators: Iterable[Operator],
                 diff_evaluator: DifferenceEvaluator, goal_state: State):
        """"""
        StateSpace.__init__(self, initial_state, operators, diff_evaluator)
        self._goal_state = goal_state

    @property
    def goal_state(self) -> State:
        """"""
        return self._goal_state

    @property
    def init_goal_equality(self) -> bool:
        """"""
        return self.difference_evaluator.are_the_same(
            self.initial_state, self.goal_state)

    def difference_from_goal(self, state: State) -> bool:
        """"""
        return self.difference(state, self.goal_state) == 0


class StateSpaceShuffle:
    """"""

    def __init__(self, goal_state: State, operators: Iterable[Operator],
                 diff_evaluator: DifferenceEvaluator, shuffle_grade: int):
        """"""

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
        """"""
        return self._shuffle_grade

    @property
    def goal_state(self) -> State:
        """"""
        return self._goal_state

    @property
    def operators(self) -> tuple[Operator]:
        """"""
        return self._operators

    @property
    def diff_evaluator(self) -> DifferenceEvaluator:
        """"""
        return self._diff_evaluator

    def shuffle(self) -> StateSpace:
        """"""
        current_state = self.goal_state
        for _ in range(self.shuffle_grade):
            applicable_ops = current_state.filter_applicable(self.operators)
            current_state = current_state.apply(choice(applicable_ops))
        return GoalOrientedStateSpace(current_state, self.operators,
                                      self.diff_evaluator, self.goal_state)




