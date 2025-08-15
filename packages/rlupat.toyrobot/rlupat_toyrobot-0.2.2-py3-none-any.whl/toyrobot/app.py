import argparse
import logging
import os
import sys

from toyrobot.models.tabletop import TableTop
from toyrobot.parser.commandparser import CommandParser


def init_logging(log_level):
    if log_level:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.CRITICAL)


def parse_args(args):
    def positive_integer(val):
        if (type(val) != int and not val.isnumeric()) or int(val) <= 0:
            raise argparse.ArgumentTypeError(f"{val} is invalid. Required positive integer value")

        return int(val)

    parser = argparse.ArgumentParser(description="Run Toy Robot Simulation")
    parser.add_argument("-i", "--input", help="file consisting of robot movement commands (required)", required=True)
    parser.add_argument("-x", "--sizeX", type=positive_integer, help="dimension of tabletop [5]", default=5)
    parser.add_argument("-y", "--sizeY", type=positive_integer, help="dimension of tabletop [5]", default=5)
    parser.add_argument("-d", "--debug", help="turn on debugging [False]", action='store_true')
    return parser.parse_args(args)


def start_app_file(args):
    cmd_parser = CommandParser()
    table_top = TableTop(args.sizeX, args.sizeY)

    if os.path.exists(args.input):
        f = open(args.input)
        for line in f:
            cmd = line.strip().split()
            cmd_parser.apply_command(table_top, cmd)
    else:
        logging.critical(f"File {args.input} does not exist")


def main():
    arg_parser = parse_args(sys.argv[1:])
    init_logging(arg_parser.debug)
    start_app_file(arg_parser)


if __name__ == "__main__":
    main()
