import random
import time
import yoke

class WormState(object):
    def reset(self, width: int, height: int):
        # Size of the play area
        self.width = width
        self.height = height

        # Initial direction is to the right
        self.dx, self.dy = 1, 0

        # Sentinel node for linked list
        self.worm = yoke.Yoke()

        # Start with the worm's head at the center
        w = yoke.Yoke()
        w.x = width // 2
        w.y = height // 2
        self.worm.insert_left(w)

        # No growth until number eaten
        self.grow_count = 0

        # Score starts at 0
        self.score = 0

        # Random number generator using current time as seed
        # TODO - allow specifying seed on command line
        self.prng = random.Random(time.time()) # Random number generator

        # Generate a target number for the worm to eat
        self.generate_target()

    def generate_target(self):
        # Generate a number between 1 and 9 for the target
        tv = self.prng.randint(1, 9)

        # Keep trying to generate a target that doesn't collide with worm
        still_searching = True
        while still_searching:
            # Generate a random, x and y for the target
            tx = self.prng.randint(0, self.width - 1)
            ty = self.prng.randint(0, self.height - 1)

            # Make sure no elements in the worm collide with the position
            w = self.worm.left
            still_searching = False
            while w != self.worm:
                if tx == w.x and ty == w.y:
                    # We have a conflict. Generate another
                    still_searching = True
                    break
                w = w.left
            
        # No collisions with worm. Safe to use generated target
        self.target_x = tx
        self.target_y = ty
        self.target_value = tv
        return

    def next_step(self):
        # Get the position of the current head and figure out new position
        w = self.worm.left
        x = w.x + self.dx
        y = w.y + self.dy

        # Create a new head and put it at the head of the list
        head = yoke.Yoke()
        head.x = x
        head.y = y
        self.worm.insert_left(head)

        # If we are not growing, delete the tail of the worm
        old_xy = None
        if self.grow_count == 0:
            tail = self.worm.right
            tail.remove()
            old_xy = (tail.x, tail.y)
        else:
            self.grow_count -= 1
        
        # If head has hit the target add to grow count and generate new target
        if self.target_x == head.x and self.target_y == head.y:
            self.grow_count += self.target_value
            self.score += self.target_value
            self.generate_target()

        return old_xy

    def go_right(self):
        self.dx, self.dy = 1, 0

    def go_left(self):
        self.dx, self.dy = -1, 0

    def go_down(self):
        self.dx, self.dy = 0, 1

    def go_up(self):
        self.dx, self.dy = 0, -1
