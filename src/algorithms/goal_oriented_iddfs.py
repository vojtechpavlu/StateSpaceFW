""""""

from .goal_oriented_blinds import GoalOrientedBlindAlgorithm
from ..fw import GoalOrientedStateSpace, State, SolutionSuccess


class GOIDDFS(GoalOrientedBlindAlgorithm):
    """"""

    __ALGO_NAME = "Goal-Oriented Iterative Deepening Depth-First Search"

    def __init__(self, state_space: GoalOrientedStateSpace,
                 algo_name: str = __ALGO_NAME, depth_increment: int = 8):
        """"""
        GoalOrientedBlindAlgorithm.__init__(self, algo_name, state_space)
        self._depth_increment = depth_increment

        if self._depth_increment < 1:
            raise Exception("Depth cannot be less than 1")

    @property
    def depth_increment(self):
        """Depth increment for which the search range is enlarged with every
        iteration."""
        return self._depth_increment

    def solve(self):
        """"""

        # Save all the operators
        all_ops = self.state_space.operators

        # Current depth
        current_depth = 0

        # Nodes deeper than current increment
        deeper_nodes: list[State] = []

        # Iterate to infinity
        while True:

            # Increasing the limit depth
            current_depth = current_depth + self.depth_increment

            # Adds a first line after the limit and purify the list
            self.safe_add_all_to_fringe(deeper_nodes)
            deeper_nodes.clear()

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

                # If it isn't equal to the goal state
                elif self.difference_from_goal(current_state) > 0:

                    # Get list of all the children states
                    children = current_state.apply_all(
                        current_state.filter_applicable(all_ops))

                    if len(current_state.parents_sequence)-1 >= current_depth:
                        """If the current state is on the edge of the limit"""
                        deeper_nodes.extend(children)

                    elif self.minimize_accesses:
                        """If the algorithm should filter only newly visited 
                        children or not. Similarly if the current state should 
                        be checked or not."""
                        self.safe_add_all_to_fringe(children)
                        self.safe_add_to_closed(current_state)

                    else:
                        """If the safety does not matter"""
                        self.add_all_to_fringe(children)
                        self.add_to_closed(current_state)

                # The current state is equivalent to the goal one
                else:
                    raise SolutionSuccess(self, current_state)

            # The solution cannot be reached; all accessible states were searched
            #raise SolutionFailure(
            #    "All states were searched and no suitable result was found", self)


    @property
    def next_from_fringe(self) -> State:
        """"""
        return self._fringe.pop()



