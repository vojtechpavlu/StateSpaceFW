""""""
from src.algorithms.goal_oriented_a_star import GOAStar
from src.algorithms.goal_oriented_best_first import GOBestFirstSearch
from src.algorithms.goal_oriented_bfs import GOBFS
from src.algorithms.goal_oriented_dfs import GODFS
from src.algorithms.goal_oriented_iddfs import GOIDDFS
from src.fw.algorithm import SolutionSuccess
from src.fw.state import State, Operator, DifferenceEvaluator
from src.fw.state_space import StateSpace, GoalOrientedStateSpace
from src.algorithms.random_operator_picker import RandomOperatorPicker


class Disk:
    """"""

    def __init__(self, disk_size: int):
        """"""
        self._size = disk_size

        if self._size < 1:
            raise Exception(f"Disk size has to be at least 1: {self._size}")

    @property
    def size(self) -> int:
        """"""
        return self._size

    def clone(self) -> "Disk":
        return Disk(self.size)

    def __repr__(self):
        return str(self.size)


class Stick:
    """"""

    def __init__(self, stick_number: int):
        """"""
        self._stick_number = stick_number
        self._disks: list[Disk] = []

    @property
    def stick_number(self) -> int:
        return self._stick_number

    @property
    def disks(self) -> tuple[Disk]:
        return tuple(self._disks)

    @property
    def has_any(self) -> bool:
        """"""
        return len(self) > 0

    def has_disk_of_size(self, size: int) -> bool:
        """"""
        for disk in self.disks:
            if disk.size == size:
                return True
        return False

    def size_of_top(self) -> int:
        """"""
        if self.has_any:
            return self.disks[-1].size
        raise Exception("No disk")

    def pop(self) -> Disk:
        """Removes and returns the disk on top."""
        return self._disks.pop()

    def append(self, disk: Disk):
        """"""
        self._disks.append(disk)

    def clone(self) -> "Stick":
        """"""
        stick = Stick(self.stick_number)
        for disk in self.disks:
            stick.append(disk.clone())
        return stick

    def check(self) -> bool:
        """"""
        if len(self) > 1:
            previous = self.disks[0]
            for disk in self.disks[1:]:
                if disk.size > previous.size:
                    return False
        return True

    def __len__(self):
        """"""
        return len(self.disks)

    def __repr__(self):
        return f"[{self.stick_number}: {self.disks}]"


class HanoiState(State):
    """"""

    def __init__(
            self, diff_evaluator: "DifferenceEvaluator",
            sticks: list[Stick], max_disk_size: int,
            parent: "HanoiState" = None, applied_operator: "Operator" = None):
        """"""

        State.__init__(self, diff_evaluator, parent, applied_operator)

        self._sticks = sticks
        self._num_of_sticks = len(sticks)
        self._max_disk_size = max_disk_size

        for stick in self.sticks:
            if not stick.check():
                raise Exception(f"Not acceptable stick state: {stick}")

    @property
    def sticks(self) -> tuple[Stick]:
        """"""
        return tuple(self._sticks)

    @property
    def num_of_sticks(self) -> int:
        """"""
        return self._num_of_sticks

    @property
    def max_disk_size(self) -> int:
        """"""
        return self._max_disk_size

    def stick_index_by_disk(self, size: int) -> int:
        """"""
        for index, stick in enumerate(self.sticks):
            if stick.has_disk_of_size(size):
                return index
        raise Exception(f"No disk of the {size=}")

    def stick(self, stick_number: int):
        for stick in self.sticks:
            if stick.stick_number == stick_number:
                return stick
        raise Exception(f"No stick with number {stick_number}")

    def clone(self) -> "HanoiState":
        sticks = []
        for stick in self.sticks:
            sticks.append(stick.clone())
        return HanoiState(self.difference_evaluator, sticks,
                          self.max_disk_size)

    def __repr__(self):
        return f"{self.sticks}"


class HanoiOperator(Operator):
    """"""

    def __init__(self, operator_name: str, from_stick: int, to_stick: int):
        Operator.__init__(self, operator_name)
        self._from_stick = from_stick
        self._to_stick = to_stick

        if from_stick < 0 or to_stick < 0:
            raise Exception(f"HanoiOperator error")

    @property
    def from_stick(self) -> int:
        return self._from_stick

    @property
    def to_stick(self) -> int:
        return self._to_stick

    def can_be_applied_on(self, state: HanoiState) -> bool:
        """"""
        if not state.stick(self.from_stick).has_any:
            return False
        elif not state.stick(self.to_stick).has_any:
            return True
        else:
            return (state.stick(self.from_stick).size_of_top() <
                    state.stick(self.to_stick).size_of_top())

    def apply_on(self, state: HanoiState) -> "HanoiState":
        """"""
        if self.can_be_applied_on(state):

            new_state = state.clone()

            from_stick = new_state.stick(self.from_stick)
            to_stick = new_state.stick(self.to_stick)
            to_stick.append(from_stick.pop())

            new_state.parent_state = state
            new_state.applied_operator = self

            return new_state
        else:
            raise Exception(f"Cannot apply '{self}' on {state}")

    def __repr__(self):
        return f"{self.from_stick}->{self.to_stick}"


class HanoiEvaluator(DifferenceEvaluator):
    """"""

    def evaluate_difference(
            self, state1: "HanoiState", state2: "HanoiState") -> float:
        """"""
        for sn in range(1, len(state1.sticks)):
            # definition of sticks
            st1 = state1.stick(sn)
            st2 = state2.stick(sn)

            # If disk number differs
            if len(st1) != len(st2):
                return 1

            # for every disk index in disks
            for dn in range(len(st1)):

                # If sizes of disks with this indexes are not equal
                if st1.disks[dn].size != st2.disks[dn].size:
                    return 1
        return 0


class HanoiFloatEvaluator(DifferenceEvaluator):
    """"""

    def evaluate_difference(self, s1: "HanoiState", s2: "HanoiState") -> float:
        """"""
        diff = 0
        for disk_size in range(1, s1.max_disk_size):
            if (s1.stick_index_by_disk(disk_size) !=
                    s2.stick_index_by_disk(disk_size)):
                diff += 1
        return diff


def init(n_disks: int = 3, n_sticks: int = 3):

    #evaluator = HanoiEvaluator()
    evaluator = HanoiFloatEvaluator()

    operators = []

    for from_stick in range(1, n_sticks + 1):
        for to_stick in range(1, n_sticks + 1):
            if from_stick != to_stick:
                operators.append(HanoiOperator(
                    f"{from_stick}->{to_stick}", from_stick, to_stick))

    start = state_gen(n_disks + 1, n_sticks + 1, evaluator, 0)
    end = state_gen(n_disks + 1, n_sticks + 1, evaluator, 2)

    return GoalOrientedStateSpace(start, operators, evaluator, end)


def state_gen(n_d: int, n_s: int, eva: DifferenceEvaluator, all_at: int):

    sticks = []

    for stick in range(1, n_s):
        sticks.append(Stick(stick))

    for disk in reversed(range(1, n_d)):
        sticks[all_at].append(Disk(disk))

    return HanoiState(eva, sticks, n_d, None, None)


# algo = RandomOperatorPicker(init(8))

disks = 5
sticks = 3

algos = [
    #RandomOperatorPicker(init(disks, sticks)),
    #GOBFS(init(disks, sticks)),
    #GODFS(init(disks, sticks)),
    #GOIDDFS(init(disks, sticks), depth_increment=2),
    #GOBestFirstSearch(init(disks, sticks)),
    GOAStar(init(disks, sticks))
]

import time

start_time = None
end_time = None

results = []

print(init(disks, sticks).initial_state)

for algo in algos:
    try:
        start_time = time.time()
        algo.solve()
    except SolutionSuccess as success:
        end_time = time.time()
        print(success.algorithm.algorithm_name)
        ops = success.final_state.operators_sequence
        print(len(ops), ":", ops)

        print("Execution time:", end_time - start_time, "seconds")

        results.append(
            (success.algorithm.algorithm_name, f"{len(ops)}",
             f"{end_time-start_time} s"))

        print(50*"-", "\n")

for r in results:
    print(f"{r[0]:55} {r[1]} operators used in {r[2]}")
