import pytest

from toyrobot.models.orientation import Orientation
from toyrobot.models.tabletop import TableTop
from toyrobot.models.robot import Robot


@pytest.fixture
def my_tabletop():
    return TableTop(5, 5)


class TestTableTop:
    @pytest.mark.parametrize("test_x, test_y, expected_outcome", [
        (0, 0, True),
        (5, 5, True),
        (5, 6, False),
        (6, 5, False),
        (-1, 3, False),
    ])
    def test_is_within_boundary(self, my_tabletop, test_x, test_y, expected_outcome):
        assert my_tabletop.is_within_boundary(test_x, test_y) == expected_outcome

    @pytest.mark.parametrize("test_x, test_y, expected_outcome", [
        (0, 0, True),
        (5, 5, True),
        (5, 6, False),
        (6, 5, False),
        (-1, 3, False),
    ])
    def test_is_valid_position(self, my_tabletop, test_x, test_y, expected_outcome):
        assert my_tabletop.is_valid_position(test_x, test_y) == expected_outcome

    @pytest.mark.parametrize("n_robot", [0, 1, 2, 3])
    def test_add_robot(self, my_tabletop, n_robot):
        for n in range(n_robot):
            my_tabletop.add_robot(Robot(n, n, "WEST"))
        assert len(my_tabletop.robot) == n_robot

    @pytest.mark.parametrize("n_robot, expected_outcome", [
        (0, False),
        (1, True),
        (2, True),
        (3, True)
    ])
    def test_has_robot(self, my_tabletop, n_robot, expected_outcome):
        for n in range(n_robot):
            my_tabletop.add_robot(Robot(n, n, "WEST"))
        assert my_tabletop.has_robot() == expected_outcome

    @pytest.mark.parametrize("n_robot, expected_outcome", [
        (1, [0, 0, Orientation.EAST]),
        (2, [0, 0, Orientation.EAST]),
        (3, [0, 0, Orientation.EAST])
    ])
    def test_passes_get_robot_default(self, my_tabletop, n_robot, expected_outcome):
        for n in range(n_robot):
            my_tabletop.add_robot(Robot(n, n, "EAST"))

        test_robot = my_tabletop.get_robot()
        test_position = [test_robot.x, test_robot.y, test_robot.orient]

        assert test_position == expected_outcome

    @pytest.mark.parametrize("n_robot, expected_outcome", [
        (1, [0, 0, Orientation.EAST]),
        (2, [1, 1, Orientation.EAST]),
        (3, [2, 2, Orientation.EAST])
    ])
    def test_passes_get_robot_multiple(self, my_tabletop, n_robot, expected_outcome):
        for n in range(n_robot):
            my_tabletop.add_robot(Robot(n, n, "EAST"))

        test_robot = my_tabletop.get_robot(n_robot - 1)
        test_position = [test_robot.x, test_robot.y, test_robot.orient]

        assert test_position == expected_outcome

    def test_fails_get_robot_multiple(self, my_tabletop):
        with pytest.raises(ValueError):
            my_tabletop.get_robot()
