""""""


from typing import Iterable
from src.fw import (State, Operator, GoalOrientedStateSpace,
                    DifferenceEvaluator, StateSpaceShuffle,
                    FringeBasedAlgorithm)


class Field:
    """"""

    def __init__(self, value: str, x: int, y: int):
        """"""

        if x < 0:
            raise Exception(f"x cannot be < 0: {x}")
        elif y < 0:
            raise Exception(f"y cannot be < 0: {y}")

        self._x = x
        self._y = y
        self._value = value

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @x.setter
    def x(self, new_x: int):
        self._x = new_x

    @y.setter
    def y(self, new_y: int):
        self._y = new_y

    @property
    def value(self) -> str:
        return self._value

    def clone(self) -> "Field":
        return Field(self.value, self.x, self.y)

    def __repr__(self):
        return f"{self.value} @ [{self.x}, {self.y}]"


class Grid(State):
    """"""

    _EMPTY = "_"

    def __init__(self, fields: Iterable[Field],
                 diff_evaluator: DifferenceEvaluator, parent: State = None,
                 operator: Operator = None, width: int = 3, height: int = 3):
        """"""
        State.__init__(self, diff_evaluator, parent, operator)

        self._fields = list(fields)
        self.__width = width
        self.__height = height

    @property
    def fields(self) -> tuple[Field]:
        return tuple(self._fields)

    @property
    def empty_field(self) -> Field:
        return self.field_by_value(self._EMPTY)

    @property
    def border_values(self) -> tuple[int, int, int, int]:
        return 0, self.__width, 0, self.__height

    def field_by_value(self, value: str) -> Field:
        for field in self.fields:
            if field.value == value:
                return field
        raise Exception(f"No field with value {value}")

    def field_by_coords(self, x: int, y: int) -> Field:
        for field in self.fields:
            if field.x == x and field.y == y:
                return field
        raise Exception(f"No field with coords [{x}, {y}]")

    def has_coords(self, x: int, y: int) -> bool:
        for field in self.fields:
            if field.x == x and field.y == y:
                return True
        return False

    def clone(self) -> "Grid":
        new_fields = []

        for field in self.fields:
            new_fields.append(field.clone())

        return Grid(new_fields, self.difference_evaluator, self.parent_state,
                    self.applied_operator, self.__width, self.__height)

    @staticmethod
    def replace(field1: Field, field2: Field):
        # Get original coords in tuple of ints
        f1_c = field1.x, field1.y
        f2_c = field2.x, field2.y

        # Save coords of other field
        field1.x = f2_c[0]
        field1.y = f2_c[1]
        field2.x = f1_c[0]
        field2.y = f1_c[1]

    def __repr__(self):
        result = ""
        for y in range(self.__height):
            for x in range(self.__width):
                result = f"{result}{self.field_by_coords(x, y).value:3} "
            result = f"{result}\n"
        return result


class ManhattanEvaluator(DifferenceEvaluator):
    """"""

    def evaluate_difference(self, g1: "Grid", g2: "Grid") -> float:
        # Total Manhattan distance between the two grids
        total_difference = 0

        # For each field in the first grid
        for f1 in g1.fields:

            # Shorthand for the field of same value in the second grid
            f2 = g2.field_by_value(f1.value)

            # Scallarize the vector of difference
            total_difference += abs(f2.x - f1.x)
            total_difference += abs(f2.y - f1.y)

        # Return result
        return total_difference


class MoveOperator(Operator):
    """"""

    def __init__(self, operator_name: str, schema: tuple[int, int]):
        Operator.__init__(self, operator_name)
        self._schema = schema

    @property
    def schema(self) -> tuple[int, int]:
        return self._schema

    def coords_of_the_other(self, x: int, y: int):
        return x + self.schema[0], y + self.schema[1]

    def can_be_applied_on(self, state: "Grid") -> bool:
        ffrom = state.empty_field
        return state.has_coords(*self.coords_of_the_other(ffrom.x, ffrom.y))

    def apply_on(self, state: "Grid") -> "Grid":
        if self.can_be_applied_on(state):
            new_s = state.clone()
            empty_f = new_s.empty_field
            dest_field = self.coords_of_the_other(empty_f.x, empty_f.y)
            new_s.replace(empty_f, new_s.field_by_coords(*dest_field))

            new_s.parent_state = state
            new_s.applied_operator = self

            return new_s

        else:
            raise Exception(f"Cannot be applied: {self=} on {state=}")


def _directions() -> tuple[str, str, str, str]:
    return "RIGHT", "UP", "LEFT", "DOWN"


def _moving_schemas() -> dict:
    return {
        _directions()[0]: (1, 0),
        _directions()[1]: (0, -1),
        _directions()[2]: (-1, 0),
        _directions()[3]: (0, 1)
    }


def operators() -> tuple[MoveOperator]:
    return tuple(map(lambda item: MoveOperator(item[0], item[1]),
                     _moving_schemas().items()))

def ordered_state(diff_eval: DifferenceEvaluator,
                  width: int = 3, height: int = 3):
    fields = [Field("_", 0, 0)]

    i = 1

    for y in range(height):
        for x in range(width):
            if x == 0 and y == 0:
                continue
            fields.append(Field(str(i), x, y))
            i += 1

    return Grid(fields, diff_eval, width=width, height=height)


def shuffle(grade: int, width: int = 3, height: int = 3,
            diff_eval=ManhattanEvaluator()):

    return StateSpaceShuffle(ordered_state(diff_eval, width, height),
                             operators(), diff_eval, grade)


def state_space_gen(init: Grid, goal: Grid) -> GoalOrientedStateSpace:
    return GoalOrientedStateSpace(
        init.clone(), operators(), ManhattanEvaluator(), goal.clone())


from src.algorithms.goal_oriented_a_star import GOAStar
from src.algorithms.goal_oriented_dfs import GODFS
from src.algorithms.goal_oriented_bfs import GOBFS
from src.algorithms.goal_oriented_best_first import GOBestFirstSearch
from src.algorithms.goal_oriented_iddfs import GOIDDFS
from src.algorithms.random_operator_picker import RandomOperatorPicker
from src.fw import SolutionSuccess


shuffler = shuffle(25)
state_space = shuffler.shuffle()
goal_state: Grid = state_space.goal_state
initial_state: Grid = state_space.initial_state
print(shuffler.applied_operators)

algos = [
    GOAStar(state_space_gen(initial_state, goal_state)),
    GOBFS(state_space_gen(initial_state, goal_state)),
    GOIDDFS(state_space_gen(initial_state, goal_state), depth_increment=2),
    GOBestFirstSearch(state_space_gen(initial_state, goal_state)),
    GODFS(state_space_gen(initial_state, goal_state)),
    RandomOperatorPicker(state_space_gen(initial_state, goal_state)),
]

start = None
print(initial_state)
print(goal_state)
for algo in algos:
    try:
        algo()
    except SolutionSuccess as success:
        algo: FringeBasedAlgorithm = algo
        print(
            algo.algorithm_name, f"visited: {algo.number_of_seen}, time: "
            f"{algo.ran_for}", f"Applied operators: "
            f"{len(success.final_state.operators_sequence)}")





