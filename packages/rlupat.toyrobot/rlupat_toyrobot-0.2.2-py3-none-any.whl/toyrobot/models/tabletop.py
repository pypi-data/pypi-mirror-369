class TableTop:
    """
    TableTop Class as the base of the simulation arena of size X and Y
    Supports hosting more than one robots (for future implementation), but require future logic re-implementation
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.robot = []

    def is_within_boundary(self, new_x, new_y):
        if (new_x >= 0) and (new_y >= 0) and (new_x <= self.x) and (new_y <= self.y):
            return True
        else:
            return False

    # Currently only checking if it is within boundary
    # Future implementation: check if it clashes with other robots' movement
    def is_valid_position(self, new_x, new_y):
        if self.is_within_boundary(new_x, new_y):
            return True

        return False

    def add_robot(self, new_robot):
        self.robot.append(new_robot)

    def has_robot(self):
        if len(self.robot) > 0:
            return True

        return False

    # By default, only returns the first robot
    # Additional placeholder for future implementation that supports multiple Robots on a single Table Top
    def get_robot(self, item=0):
        if item < len(self.robot):
            return self.robot[item]
        else:
            raise ValueError(f"Accessing invalid Robot[{item}] that is not on the Table Top")

