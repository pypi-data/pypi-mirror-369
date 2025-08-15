from toyrobot.models.orientation import Orientation


class Robot:
    def __init__(self, x, y, orient):
        self.x, self.y, self.orient = self.place(x, y, orient)

    def move(self):
        next_x = self.x + self.orient.value[0]
        next_y = self.y + self.orient.value[1]

        return next_x, next_y

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def left(self):
        self.orient = self.orient.left()

    def right(self):
        self.orient = self.orient.right()

    def place(self, x, y, orient):
        self.x = x
        self.y = y

        # Check if user's input for orientation is valid under the defined Orientation enum
        # Is not required if this is called from the main.app (should have been caught by command parser validator)
        if orient in Orientation.__members__:
            self.orient = Orientation[orient]
        else:
            raise ValueError(f"Invalid Robot Orientation ${orient}. Supported values: {list(Orientation.__members__)} ")

        return self.x, self.y, self.orient

    def report(self):
        print(f"{self.x},{self.y},{self.orient.name}")
