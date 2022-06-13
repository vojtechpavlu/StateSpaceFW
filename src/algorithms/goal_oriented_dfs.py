""""""

from .goal_oriented_blinds import GoalOrientedBlindAlgorithm
from ..fw import GoalOrientedStateSpace, State


class GODFS(GoalOrientedBlindAlgorithm):
    """"""

    __ALGO_NAME = "Goal-Oriented Depth-first search"

    def __init__(self, state_space: GoalOrientedStateSpace,
                 algo_name: str = __ALGO_NAME):
        GoalOrientedBlindAlgorithm.__init__(self, algo_name, state_space)

    @property
    def next_from_fringe(self) -> State:
        """"""
        return self._fringe.pop()



