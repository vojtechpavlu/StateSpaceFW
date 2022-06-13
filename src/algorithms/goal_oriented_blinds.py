""""""

from ..fw import (GoalBasedAlgorithm, FringeBasedAlgorithm,
                  SolutionSuccess, SolutionFailure, GoalOrientedStateSpace)


class GoalOrientedBlindAlgorithm(FringeBasedAlgorithm, GoalBasedAlgorithm):
    """"""

    def __init__(self, algo_name: str, state_space: GoalOrientedStateSpace,
                 minimize_accesses: bool = True):
        FringeBasedAlgorithm.__init__(self, algo_name, state_space)
        GoalBasedAlgorithm.__init__(self, algo_name, state_space)
        self._minimize_accesses = minimize_accesses

    @property
    def minimize_accesses(self) -> bool:
        """If the algorithm should try to minimize the accesses to some states.
        The mechanism is done by checking if it was searched in the current
        state (or equal one)."""
        return self._minimize_accesses

    def solve(self):
        """"""

        # Check if the initial is equivalent to goal
        if self.state_space.init_goal_equality:
            raise SolutionSuccess(self, self.state_space.initial_state)

        # Save all the operators
        all_ops = self.state_space.operators

        # While the list of states to be searched is not emtpy
        while self.has_any_in_fringe:

            # Pick another from the fringe
            current_state = self.next_from_fringe

            """If the algorithm should minimize the accesses, the current
            state is checked by the algorithm if it wasn't searched in 
            already. If it was, it continues by another state without 
            further elaboration on that one."""
            if self.minimize_accesses and self.is_in_closed(current_state):
                continue

            else:
                # Get list of all the children states
                children = current_state.apply_all(
                    current_state.filter_applicable(all_ops))

                # Check if any of the child nodes is equivalent to goal one
                for child_node in children:
                    if self.difference_from_goal(child_node) == 0:
                        raise SolutionSuccess(self, child_node)

                """If the algorithm should filter only newly visited 
                children or not. Similarly if the current state should 
                be checked or not."""
                if self.minimize_accesses:
                    self.safe_add_all_to_fringe(children)
                    self.safe_add_to_closed(current_state)
                else:
                    self.add_all_to_fringe(children)
                    self.add_to_closed(current_state)

        # The solution cannot be reached; all accessible states were searched
        raise SolutionFailure(
            "All states were searched and no suitable result was found", self)

