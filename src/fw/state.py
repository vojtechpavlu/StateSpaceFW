"""This module contains the definition of the most general abstractions of
the State, Operator and DifferenceEvaluator.

These classes define the general protocol of the main objects in state space
and the critical means of the state space problem solutions.
"""

from abc import ABC, abstractmethod
from typing import Iterable


class State(ABC):
    """This abstract class represents possible state the system can be in."""

    def __init__(self, diff_evaluator: "DifferenceEvaluator",
                 parent: "State" = None, applied_operator: "Operator" = None):
        """General initor of the state. Usually are states created in two main
        situations:

            - When starting the search for solution (parent is None, so is the
              applied operator)

            - When is created a new state the state space is in by applying
              an operator on parent state

        Parameters
        ----------
        diff_evaluator : DifferenceEvaluator
            Evaluator used to quantify the difference between two states. When
            the difference is equal to zero, the system assumes the two states
            are equal. This instance of evaluator is usually mutual for all the
            states in state space.

        parent : State
            Ancestor of this state; this state is created by application of
            an operator to the parent or as an initial state (without parent).
            None by default.

        applied_operator : Operator
            Reference to instance of Operator, which was applied on the parent
            state to produce this instance. None by default.
        """
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

        # While the current state has a parent (ie is not initial state)
        while current_state.parent_state:

            # Save the applied operator which result was current state creation
            operators.append(current_state.applied_operator)

            # Set current state as the parent
            current_state = current_state.parent_state

        # Return the reversed list of operators in tuple
        return tuple(reversed(operators))

    def filter_applicable(
            self, operators: "Iterable[Operator]") -> "tuple[Operator]":
        """Method filtering only the applicable operators (instances of the
        class 'Operator'). Those operators which cannot be applied are omitted.
        The result is formed in a tuple.

        Parameters
        ----------
        operators : Iterable[Operator]
            Any iterable collection where there are contained operators to be
            filtered by it's possibility to be applied on this state.

        Returns
        -------
        tuple[Operator]
            Tuple of all operators which can be applied to this current state.
        """
        return tuple(filter(lambda o: self.can_be_applied(o), operators))

    def can_be_applied(self, operator: "Operator") -> bool:
        """Method returning boolean information about availability of the
        given operator application on this state. When the operator can be
        applied on it, returns True, else False.

        For the determination of the applicability, the operator's internal
        logic is used.

        Parameters
        ----------
        operator : Operator
            Operator to be tested if it is applicable on this state instance.

        Returns
        -------
        bool
            If the given operator can or cannot be applied on this state
        """
        return operator.can_be_applied_on(self)

    def apply(self, operator: "Operator") -> "State":
        """Method tries to apply an operator on this state. This produces a
        new state.

        Parameters
        ----------
        operator : Operator
            Actual operator to be applied on this state. As a result of this
            application is created a new state.

        Returns
        -------
        State
            The state created by the application of the given operator on this
            state. This new state is a child of this one.

        Raises
        ------
        OperatorApplicationError
            When the given operator to be applied is considerate as not
            available step.
        """
        if self.can_be_applied(operator):
            return operator.apply_on(self)

        # When the operator cannot be applied, raise error
        raise OperatorApplicationError(
            operator, self, f"Cannot apply operator {operator} on {self}")

    def apply_all(self, operators: "Iterable[Operator]") -> "tuple[State]":
        """Method tries to apply all the given operators on this state. It
        results in a tuple of states.

        Only applicable operators are applied. Others are omitted.

        Parameters
        ----------
        operators : Iterable[Operator]
            Iterable collection of operators to be applied. This collection
            is filtered for the applicable only ones. Each of the valid one
            produces one state.

        Returns
        -------
        tuple[State]
            Tuple of states created while applying the given operator on this
            state.
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
        """Initor of the Operator taking the operator name only. This is name
        is used to distinguish various operators and understand the solution.

        Parameters
        ----------
        operator_name : str
            Human-readable name of the operator used to distinguish various
            operators and to understand the solution.
        """
        self._name = operator_name

    @property
    def operator_name(self) -> str:
        """Property returns name of the operator."""
        return self._name

    @abstractmethod
    def can_be_applied_on(self, state: "State") -> bool:
        """This abstract method defines the protocol of returning an
        information about the possibility of the application of this operator
        on the given state.

        Parameters
        ----------
        state : State
            State for which the operator checks it's availability.

        Returns
        -------
        bool
            If the operation application would result in inconsistent state,
            the return value is False, else True.
        """

    @abstractmethod
    def apply_on(self, state: "State") -> "State":
        """Abstract method which tries to apply this operator on given state.
        This operation results in a new (child) state creation.

        Parameters
        ----------
        state : State
            State this operator should be applied on

        Returns
        -------
        State
            State created by the operator application. This new state is a
            child of the given state.
        """

    def __repr__(self):
        """"""
        return self.operator_name


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


class OperatorApplicationError(Exception):
    """"""

    # Private general message about not-availability of the application
    __MSG = "Operator cannot be applied"

    def __init__(self, operator: Operator, state: State, message: str = __MSG):
        """"""
        Exception.__init__(self, message)
        self._operator = operator
        self._state = state

    @property
    def operator(self) -> Operator:
        """"""
        return self._operator

    @property
    def state(self) -> State:
        """"""
        return self._state





