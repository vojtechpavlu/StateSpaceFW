""""""

from .goal_oriented_blinds import GoalOrientedBlindAlgorithm
from ..fw import GoalOrientedStateSpace, State


class GOBFS(GoalOrientedBlindAlgorithm):
    """"""

    __ALGO_NAME = "Goal-Oriented Breadth-first search"

    def __init__(self, state_space: GoalOrientedStateSpace,
                 algo_name: str = __ALGO_NAME):
        GoalOrientedBlindAlgorithm.__init__(self, algo_name, state_space)

    @property
    def next_from_fringe(self) -> State:
        """"""
        return self._fringe.pop(0)



