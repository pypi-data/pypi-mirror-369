import pytest
from toyrobot.models.robot import Orientation


class TestOrientation:
    @pytest.mark.parametrize("orig_orient, expected_orient", [
        (Orientation.NORTH, Orientation.EAST),
        (Orientation.EAST, Orientation.SOUTH),
        (Orientation.SOUTH, Orientation.WEST),
        (Orientation.WEST, Orientation.NORTH),
    ])
    def test_right(self, orig_orient, expected_orient):
        assert orig_orient.right() == expected_orient

    @pytest.mark.parametrize("orig_orient, expected_orient", [
        (Orientation.NORTH, Orientation.WEST),
        (Orientation.EAST, Orientation.NORTH),
        (Orientation.SOUTH, Orientation.EAST),
        (Orientation.WEST, Orientation.SOUTH),
    ])
    def test_left(self, orig_orient, expected_orient):
        assert orig_orient.left() == expected_orient
