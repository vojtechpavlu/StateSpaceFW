""""""

from random import choice
from ..fw import GoalOrientedStateSpace, GoalBasedAlgorithm, SolutionSuccess


class RandomOperatorPicker(GoalBasedAlgorithm):

    def __init__(self, state_space: GoalOrientedStateSpace):
        GoalBasedAlgorithm.__init__(self, "RandomOperatorPicker", state_space)

    def solve(self):

        # All operators available
        ops = self.state_space.operators

        # Current state the space is in
        current_state = self.state_space.initial_state

        # While there is difference between the current state and the goal
        while self.state_space.difference_from_goal(current_state) > 0:

            # Randomly pick available operator
            applying = choice(current_state.filter_applicable(ops))

            # Apply this operator to current state and save the result
            current_state = current_state.apply(applying)

        # If the difference is zero
        raise SolutionSuccess(self, current_state)



