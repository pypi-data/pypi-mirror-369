import pytest
from toyrobot.app import parse_args, start_app_file


@pytest.mark.parametrize("argv, exp_input_file, exp_x, exp_y", [
    (["-i", "test.txt"], "test.txt", 5, 5),
    (["-i", "test/test.txt", "-x", "1"], "test/test.txt", 1, 5),
    (["-i", "test/test.txt", "--sizeX", "4", "-y", "1"], "test/test.txt", 4, 1),
])
def test_passes_parse_args(argv, exp_input_file, exp_x, exp_y):
    args = parse_args(argv)
    assert (args.input == exp_input_file) and (args.sizeX == exp_x) and (args.sizeY == exp_y)


@pytest.mark.parametrize("argv", [
    ([]),
    (["-i", "test.txt", "-a"]),
    (["-i", "test.txt", "-x", "-1"]),
    (["-i", "test.txt", "-x", "1", "--sizeY", "0"]),
    (["-i", "test.txt", "--sizeX", "abc", "--sizeY", "0x"]),
])
def test_fails_parse_args(argv):
    with pytest.raises(SystemExit):
        parse_args(argv)


@pytest.mark.parametrize("argv, expected_outcome", [
    (["-i", "resources/test1.txt"], "0,1,NORTH\n"),
    (["-i", "resources/test2.txt"], "0,0,WEST\n"),
    (["-i", "resources/test3.txt"], "3,3,NORTH\n"),
    (["-i", "resources/test4.txt"], ""),
])
def test_start_app_file(argv, expected_outcome, capsys):
    arg_parser = parse_args(argv)
    start_app_file(arg_parser)

    captured = capsys.readouterr()
    assert captured.out == expected_outcome
