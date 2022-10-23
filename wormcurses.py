import curses
import types

import wormstate

"""
The screen will be divided into the following areas:

 Grow By: x                                                        Score: xxxx
+-----------------------------------------------------------------------------+
|                                                                             |
|                                Play area                                    |
|                                                                             |
+-----------------------------------------------------------------------------+
                    Comments: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
"""

# Constants that can be used in a match statement
keys = types.SimpleNamespace()
keys.TIMEOUT = -1
keys.KEY_h = ord('h')
keys.KEY_H = ord('H')
keys.KEY_j = ord('j')
keys.KEY_J = ord('J')
keys.KEY_k = ord('k')
keys.KEY_K = ord('K')
keys.KEY_l = ord('l')
keys.KEY_L = ord('L')
keys.KEY_q = ord('q')
keys.KEY_Q = ord('Q')
keys.KEY_CTRL_L = ord('L') - 64

class WormCurses(object):
    def set_state(self, state: wormstate.WormState):
        self.state = state

    def setup_curses(self):
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.timeout(1000)

    def teardown_curses(self):
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def draw_static_content(self):
        # Clear the entire screen
        self.stdscr.clear()

        # Draw header row labels
        self.stdscr.addstr(0, 1, "Grow By:")
        self.stdscr.addstr(0, self.maxx - 12, "Score:")

        # Draw a border around the play area
        border_area = self.stdscr.subwin(self.maxy - 2, self.maxx, 1, 0)
        border_area.box()
        self.stdscr.noutrefresh()

    def safe_addch(self, y, x, c):
        try:
            self.play_area.addch(y, x, c)
        except curses.error:
            pass

    def draw_target(self):
        x = self.state.target_x
        self.play_area.addch(self.state.target_y, self.state.target_x,
             str(self.state.target_value))

    def draw_score(self):
        self.stdscr.addstr(0, self.maxx - 5, str(self.state.score).ljust(4))

    def draw_worm_full(self):
        w = self.state.worm.left
        c = '@'
        while w != self.state.worm:
            self.safe_addch(w.y, w.x, c)
            c = 'o'
            w = w.left

    def draw_worm_update(self, old_xy):
        w = self.state.worm.left
        self.safe_addch(w.y, w.x, '@')
        w = w.left
        if w != self.state.worm:
            self.safe_addch(w.y, w.x, 'o')
        if (old_xy != None):
            x, y = old_xy
            self.safe_addch(y, x, ' ')

    def draw_status(self, status):
        try:
            y = self.maxy - 1
            x = (self.maxx - len(status)) // 2
            self.stdscr.move(y, 0)
            self.stdscr.deleteln()
            self.stdscr.addstr(y, x, status)
        except curses.error:
            pass

    def next_step(self):
        old_xy = self.state.next_step()
        self.draw_target()
        self.draw_worm_update(old_xy)
        self.draw_score()
        self.draw_status(f"Iterations {self.counter}.")
        self.counter += 1
        self.play_area.refresh()
        self.stdscr.refresh()

    def draw_all(self):
        self.draw_static_content()
        self.draw_score()
        self.stdscr.refresh()
        self.draw_target()
        self.draw_worm_full()
        self.play_area.refresh()
 
    def reset_all(self):
        # Get the size of the total screen 
        (self.maxy, self.maxx) = self.stdscr.getmaxyx()

        # The first line of the screen will hold the score and growth count
        self.top_line = 0
        self.score_col = self.maxx - 11
        self.growth_col = 1

        # The game area
        self.play_area = self.stdscr.subwin(2, 1)
        self.play_maxx = self.maxx - 2  # account for border on both sides
        self.play_maxy = self.maxy - 4  # account for border, header, and footer
        self.state.reset(width = self.maxx - 2, height = self.maxy - 4)

        # Draw everything
        self.draw_all()

    def run(self):
        self.counter = 0
        try:
            self.setup_curses()
            self.reset_all()
            while True:
                ch = self.stdscr.getch()
                match ch:
                    case keys.TIMEOUT:
                        self.next_step()
                    case keys.KEY_h | keys.KEY_H | curses.KEY_LEFT:
                        self.state.go_left()
                        self.next_step()
                    case keys.KEY_j | keys.KEY_J | curses.KEY_DOWN:
                        self.state.go_down()
                        self.next_step()
                    case keys.KEY_k | keys.KEY_K | curses.KEY_UP:
                        self.state.go_up()
                        self.next_step()
                    case keys.KEY_l | keys.KEY_L | curses.KEY_RIGHT:
                        self.state.go_right()
                        self.next_step()
                    case keys.KEY_CTRL_L | curses.KEY_REFRESH:
                        self.draw_all()
                    case keys.KEY_q | keys.KEY_Q:
                        return
                    case _:
                        self.draw_status(f"Key is {ch}")
        finally:
            self.teardown_curses()