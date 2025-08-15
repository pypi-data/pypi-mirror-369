from enum import Enum


class Orientation(Enum):
    """
    Orientation Class as an enumeration for all four orientations (NORTH, EAST, SOUTH, WEST)
    The name of the enum member is identical to the string provided by the user.
    The value of the enum member represents the direction of movement, relative to coordinate (x, y).
    """

    NORTH = (0, 1)
    EAST = (1, 0)
    SOUTH = (0, -1)
    WEST = (-1, 0)

    def right(self):
        all_element = list(self.__class__)
        index = all_element.index(self) + 1
        if index >= len(all_element):
            index = 0
        return all_element[index]

    def left(self):
        all_element = list(self.__class__)
        index = all_element.index(self) - 1
        if index < 0:
            index = len(all_element) - 1
        return all_element[index]
