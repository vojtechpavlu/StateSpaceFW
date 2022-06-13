""""""

from .goal_oriented_blinds import GoalOrientedBlindAlgorithm
from ..fw import GoalOrientedStateSpace, State

class GOAStar(GoalOrientedBlindAlgorithm):
    """"""

    __ALGO_NAME = "Goal-Oriented A*"

    def __init__(self, state_space: GoalOrientedStateSpace,
                 algo_name: str = __ALGO_NAME):
        GoalOrientedBlindAlgorithm.__init__(self, algo_name, state_space)

    def _further_state_evaluation(self, state: State) -> float:
        """"""
        return (self.difference_from_goal(state) +
                len(state.parents_sequence))

    @property
    def next_from_fringe(self) -> State:
        """"""
        lowest_state = 0
        lowest_val = self._further_state_evaluation(self.fringe[0])
        for index, state in enumerate(self.fringe[1:]):
            if self._further_state_evaluation(state) <= lowest_val:
                lowest_state = index
        return self._fringe.pop(lowest_state)




