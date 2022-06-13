""""""

from .goal_oriented_blinds import GoalOrientedBlindAlgorithm
from ..fw import GoalOrientedStateSpace, State


class GOBestFirstSearch(GoalOrientedBlindAlgorithm):
    """"""

    __ALGO_NAME = "Goal-Oriented Best-first search"

    def __init__(self, state_space: GoalOrientedStateSpace,
                 algo_name: str = __ALGO_NAME):
        GoalOrientedBlindAlgorithm.__init__(self, algo_name, state_space)

    @property
    def next_from_fringe(self) -> State:
        """"""
        lowest_state = 0
        lowest_val = self.difference_from_goal(self.fringe[lowest_state])
        for index, state in enumerate(self.fringe[1:]):
            if self.difference_from_goal(state) < lowest_val:
                lowest_state = index
        return self._fringe.pop(lowest_state)




