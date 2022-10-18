import yoke

class WormState(object):
    def __init__(self):
        pass

    def reset(self, width: int, height: int):
        self.width = width                  # Width of the play area
        self.height = height                # Height of the play area
        self.dx, self.dy = 1, 0             # Initial direction is to the right
        self.worm = yoke.Yoke(None)         # Sentinel node for linked list
        headXY = (width // 2, height // 2)  # Start with the worm's head at the center
        self.worm.insert_left(yoke.Yoke(headXY))
        self.grow_count = 0                 # Start moving to the right

    def next_step(self):
        x, y = self.worm.left.value
        x += self.dx
        y += self.dy

    def go_right(self):
        self.dx, self.dy = 1, 0
        self.next_step()

    def go_left(self):
        self.dx, self.dy = -1, 0
        self.next_step()

    def go_down(self):
        self.dx, self.dy = 0, 1
        self.next_step()

    def go_up(self):
        self.dx, self.dy = 0, -1
        self.next_step()