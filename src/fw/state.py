""""""

from abc import ABC, abstractmethod
from typing import Iterable


class State(ABC):
    """This abstract class represents possible state the system can be in."""

    def __init__(self, diff_evaluator: "DifferenceEvaluator",
                 parent: "State" = None, applied_operator: "Operator" = None):
        """"""
        self._parent = parent
        self._applied_operator = applied_operator
        self._diff_evaluator = diff_evaluator

    @property
    def parent_state(self) -> "State":
        """State, on which was applied an operator and produced this state."""
        return self._parent

    @parent_state.setter
    def parent_state(self, parent: "State"):
        """Sets the parent, which this instance is was created from."""
        self._parent = parent

    @property
    def applied_operator(self) -> "Operator":
        """Operator applied on parent state, which resulted in this state."""
        return self._applied_operator

    @applied_operator.setter
    def applied_operator(self, operator: "Operator"):
        """Sets the given operator as the one applied on parent state."""
        self._applied_operator = operator

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

    @property
    def operators_sequence(self) -> "tuple[Operator]":
        """Returns all the applied operators from the initial state to this
        one. These operators are formed in a tuple."""
        current_state = self
        operators = []
        while current_state.parent_state:
            operators.append(current_state.applied_operator)
            current_state = current_state.parent_state
        return tuple(reversed(operators))

    def filter_applicable(
            self, operators: "Iterable[Operator]") -> "tuple[Operator]":
        """Method filtering only the applicable operators (instances of the
        class 'Operator'). Those operators which cannot be applied are omitted.
        The result is formed in a tuple.
        """
        return tuple(filter(lambda o: self.can_be_applied(o), operators))

    def can_be_applied(self, operator: "Operator") -> bool:
        """"""
        return operator.can_be_applied_on(self)

    def apply(self, operator: "Operator") -> "State":
        """Method tries to apply an operator on this state. This produces a
        new state."""
        if self.can_be_applied(operator):
            return operator.apply_on(self)
        raise Exception(f"Cannot apply operator {operator} on {self}")

    def apply_all(self, operators: "Iterable[Operator]") -> "tuple[State]":
        """Method tries to apply all the given operators on this state. It
        results in a tuple of states.

        Only applicable operators are applied. Others are omitted.
        """
        return tuple(map(
            lambda o: self.apply(o), self.filter_applicable(operators)))


class Operator(ABC):
    """Operator is an abstract class defining the base protocol of the
    transition from one state to another. The main principle of this
    construction is that application of the operator on a state produces
    another state.
    """

    def __init__(self, operator_name: str):
        """"""
        self._name = operator_name

    @property
    def operator_name(self) -> str:
        """Property returns name of the operator."""
        return self._name

    @abstractmethod
    def can_be_applied_on(self, state: "State") -> bool:
        """This abstract method defines the protocol of returning an
        information about the possibility of the application of this operator
        on the given state."""

    @abstractmethod
    def apply_on(self, state: "State") -> "State":
        """"""


class DifferenceEvaluator(ABC):
    """"""

    def are_the_same(self, state1: "State", state2: "State") -> bool:
        """Method able to evaluate if the two given states are the same. The
        equality of the states is True if and only if the calculated difference
        between the two states is zero (0). Otherwise it returns False.
        """
        return self.evaluate_difference(state1, state2) == 0

    @abstractmethod
    def evaluate_difference(self, state1: "State", state2: "State") -> float:
        """Abstract method defining the signature of evaluation of the
        difference between two states.

        The assumption is that the difference is always greater or equal to
        zero (0) and that when the difference is equal to zero (0), the two
        given states are equal in means of this evaluator."""
