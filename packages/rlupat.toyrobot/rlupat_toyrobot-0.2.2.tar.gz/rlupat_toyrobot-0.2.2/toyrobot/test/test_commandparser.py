import pytest
from toyrobot.parser.commandparser import CommandParser
from toyrobot.models.tabletop import TableTop
from toyrobot.models.orientation import Orientation


@pytest.fixture
def my_parser():
    return CommandParser()


@pytest.fixture
def my_tabletop():
    return TableTop(5, 5)


class TestCommandParser:
    @pytest.mark.parametrize("cmd, expected_outcome", [
        (["PLACE", "1,1,NORTH"], ["1", "1", "NORTH"]),
        (["PLACE", "a, b, north "], ["a", " b", " north"]),
        (["PLACE", "1"], ["1"]),
        (["PLACE", "1,1"], ["1", "1"]),
    ])
    def test__parse_place_cmd_string(self, my_parser, cmd, expected_outcome):
        assert my_parser._parse_place_cmd_string(cmd) == expected_outcome

    @pytest.mark.parametrize("cmd, expected_outcome", [
        (["PLACE", "1,1,NORTH"], (1, 1, "NORTH")),
        (["PLACE", "0,4,SOUTH"], (0, 4, "SOUTH")),
    ])
    def test__get_place_cmd_elements(self, my_parser, cmd, expected_outcome):
        assert my_parser._get_place_cmd_elements(cmd) == expected_outcome

    @pytest.mark.parametrize("cmd, expected_outcome", [
        (["PLACE", "1,1,NORTH"], True),
        (["MOVE", "a, b, north "], True),
        (["LEFT"], True),
        (["RIGHT", "1,1"], True),
        (["REPORT", "1,1"], True),
        (["PLACE"], True),
        (["place", "3,3,SOUTH"], False),
        (["random", "1,1"], False),
        ([], False),
    ])
    def test_is_valid_base_command(self, my_parser, cmd, expected_outcome):
        assert my_parser.is_valid_base_command(cmd) == expected_outcome

    @pytest.mark.parametrize("cmd, expected_outcome", [
        (["PLACE", "1,1,NORTH"], True),
        (["PLACE", "1,1,north "], False),
        (["PLACE", "1, 1, NORTH"], False),
        (["PLACE", "1,1"], False),
    ])
    def test_is_valid_place_command(self, my_parser, cmd, expected_outcome):
        assert my_parser.is_valid_place_command(cmd) == expected_outcome

    @pytest.mark.parametrize("cmd, expected_outcome", [
        (["PLACE", "0,0,NORTH"], True),
        (["PLACE", "6,7,NORTH"], False),
        (["LEFT"], False),
        (["RIGHT"], False),
        (["MOVE"], False),
        (["PLACE", "0,0,north"], False),
        (["random"], False),
    ])
    def test_apply_command_first_single_cmd(self, my_parser, my_tabletop, cmd, expected_outcome):
        my_parser.apply_command(my_tabletop, cmd)
        assert my_tabletop.has_robot() == expected_outcome

    @pytest.mark.parametrize("cmd, expected_outcome", [
        (["PLACE", "1,1,NORTH"], [1, 1, Orientation.NORTH]),
        (["PLACE", "6,7,NORTH"], [0, 0, Orientation.NORTH]),
        (["LEFT"], [0, 0, Orientation.WEST]),
        (["RIGHT"], [0, 0, Orientation.EAST]),
        (["MOVE"], [0, 1, Orientation.NORTH]),
        (["PLACE", "2,2,north"], [0, 0, Orientation.NORTH]),
        (["random"], [0, 0, Orientation.NORTH]),
    ])
    def test_apply_command_with_prior_place(self, my_parser, my_tabletop, cmd, expected_outcome):
        my_parser.apply_command(my_tabletop, ["PLACE", "0,0,NORTH"])
        my_parser.apply_command(my_tabletop, cmd)
        my_robot = my_tabletop.get_robot()
        assert [my_robot.x, my_robot.y, my_robot.orient] == expected_outcome

    @pytest.mark.parametrize("cmd_list, expected_outcome", [
        ([["PLACE", "1,1,NORTH"], ["PLACE", "6,7,NORTH"]], [1, 1, Orientation.NORTH]),
        ([["MOVE"], ["PLACE", "2,2,NORTH"], ["LEFT"]], [2, 2, Orientation.WEST]),
        ([["random"], ["PLACE", "1,1,EAST"], ["MOVE"]], [2, 1, Orientation.EAST]),
    ])
    def test_passes_apply_command_multiple_cmds(self, my_parser, my_tabletop, cmd_list, expected_outcome):
        for cmd in cmd_list:
            my_parser.apply_command(my_tabletop, cmd)
        my_robot = my_tabletop.get_robot()
        assert [my_robot.x, my_robot.y, my_robot.orient] == expected_outcome

    @pytest.mark.parametrize("cmd_list, expected_outcome", [
        ([["PLACE", "1,1,NORTH"], ["PLACE", "6,7,NORTH"]], True),
        ([["PLACE", "6,7,NORTH"], ["LEFT"]], False),
        ([["LEFT"], ["RIGHT"]], False),
        ([["RIGHT"], ["MOVE"]], False),
        ([["MOVE"], ["PLACE", "2,2,north"]], False),
        ([["PLACE", "2,2,north"], ["random"]], False),
        ([["random"], ["PLACE", "1,1,NORTH"]], True),
    ])
    def test_fails_apply_command_multiple_cmds(self, my_parser, my_tabletop, cmd_list, expected_outcome):
        for cmd in cmd_list:
            my_parser.apply_command(my_tabletop, cmd)
        assert my_tabletop.has_robot() == expected_outcome

    @pytest.mark.parametrize("cmd_list, expected_outcome", [
        ([["PLACE", "1,1,NORTH"], ["PLACE", "6,7,NORTH"], ["REPORT"]], "1,1,NORTH\n"),
        ([["MOVE"], ["REPORT"], ["PLACE", "2,2,NORTH"], ["LEFT"]], ""),
        ([["random"], ["PLACE", "1,1,EAST"], ["REPORT"], ["MOVE"], ["REPORT"]], "1,1,EAST\n2,1,EAST\n"),
    ])
    def test_apply_command_report(self, my_parser, my_tabletop, cmd_list, expected_outcome, capsys):
        for cmd in cmd_list:
            my_parser.apply_command(my_tabletop, cmd)
        captured = capsys.readouterr()
        assert captured.out == expected_outcome
