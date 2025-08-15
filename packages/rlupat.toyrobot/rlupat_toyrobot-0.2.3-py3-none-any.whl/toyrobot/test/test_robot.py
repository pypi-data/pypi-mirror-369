import pytest
from toyrobot.models.robot import Robot
from toyrobot.models.orientation import Orientation


@pytest.fixture
def my_robot():
    # Robot Initial Position and Orientation
    return Robot(2, 2, "NORTH")

class TestRobot:
    def test_move(self, my_robot):
        assert my_robot.move() == (2, 3)

    def test_update_position(self, my_robot):
        my_robot.update_position(3, 4)
        assert (my_robot.x == 3) and (my_robot.y == 4)

    def test_left(self, my_robot):
        my_robot.left()
        assert my_robot.orient == Orientation.WEST

    def test_right(self, my_robot):
        my_robot.right()
        assert my_robot.orient == Orientation.EAST

    def test_place(self, my_robot):
        my_robot.place(1, 4, "SOUTH")
        assert (my_robot.x == 1) and (my_robot.y == 4) and (my_robot.orient == Orientation.SOUTH)

    def test_report(self, my_robot, capsys):
        my_robot.report()
        captured = capsys.readouterr()
        assert captured.out == "2,2,NORTH\n"
