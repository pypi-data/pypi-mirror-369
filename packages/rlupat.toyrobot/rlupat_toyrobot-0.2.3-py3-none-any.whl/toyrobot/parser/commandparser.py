from toyrobot.models.orientation import Orientation
from toyrobot.models.robot import Robot
import logging


class CommandParser:
    def __init__(self):
        self.valid_commands = ["PLACE", "LEFT", "RIGHT", "MOVE", "REPORT"]

    def _parse_place_cmd_string(self, cmd):
        return cmd[1].strip().split(",")

    def _get_place_cmd_elements(self, cmd):
        x, y, orient = self._parse_place_cmd_string(cmd)
        return int(x), int(y), orient

    def is_valid_base_command(self, cmd):
        if len(cmd) < 1:
            logging.error(f"{cmd} is empty")
            return False

        if cmd[0] not in self.valid_commands:
            logging.error(f"{cmd[0]} is not valid. Accepted commands are {self.valid_commands}")
            return False

        return True

    def is_valid_place_command(self, cmd):
        invalid_place_messages = f"PLACE command requires position and orientation. (e.g PLACE 0,0,NORTH). " \
                                 f"position has to be numeric, comma-separated with no spaces, " \
                                 f"and valid orientations are {list(Orientation.__members__)}. {cmd} is not valid" \

        if len(cmd) < 2:
            logging.error(invalid_place_messages)
            return False

        else:
            position = self._parse_place_cmd_string(cmd)
            if len(position) != 3:
                logging.error(invalid_place_messages)
                return False

            else:
                x, y, orient = position
                if (not x.isnumeric()) or (not y.isnumeric):
                    logging.error(invalid_place_messages)
                    return False

                if orient not in Orientation.__members__:
                    logging.error(invalid_place_messages)
                    return False

        return True

    def apply_command(self, table_top, cmd):
        if self.is_valid_base_command(cmd):
            base_cmd = cmd[0]

            # ignore any other commands until the first robot is placed (first PLACE command)
            if not table_top.has_robot():
                if base_cmd == "PLACE":
                    if self.is_valid_place_command(cmd):
                        x, y, orient = self._get_place_cmd_elements(cmd)

                        if table_top.is_valid_position(x, y):
                            robot = Robot(x, y, orient)
                            table_top.add_robot(robot)

            else:
                active_robot = table_top.get_robot()

                if base_cmd == "PLACE":
                    if self.is_valid_place_command(cmd):
                        x, y, orient = self._get_place_cmd_elements(cmd)

                        if table_top.is_valid_position(x, y):
                            active_robot.place(x, y, orient)

                elif base_cmd == "LEFT":
                    active_robot.left()

                elif base_cmd == "RIGHT":
                    active_robot.right()

                elif base_cmd == "MOVE":
                    new_x, new_y = table_top.get_robot().move()
                    if table_top.is_valid_position(new_x, new_y):
                        active_robot.update_position(new_x, new_y)

                elif base_cmd == "REPORT":
                    active_robot.report()
