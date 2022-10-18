import curses
from time import sleep

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
        self.stdscr.addstr(0, self.maxx - 11, "Score:")

        # Draw a border around the play area
        border_area = self.stdscr.subwin(self.maxy - 2, self.maxx, 1, 0)
        border_area.box()

    def draw_full_worm():
        pass

    def reset_all(self):
        # Get the size of the total screen 
        (self.maxy, self.maxx) = self.stdscr.getmaxyx()
        self.draw_static_content()

        # The first line of the screen will hold the score and growth count
        self.top_line = 0
        self.score_col = self.maxx - 11
        self.growth_col = 1

        # The game area
        self.play_area = self.stdscr.subwin(2, 1)
        self.play_maxx = self.maxx - 2
        self.play_maxy = self.maxy - 4
        self.state.reset(width = self.maxx - 2, height = self.maxy - 4)
        for x in range(self.state.width):
            for y in range(self.state.height):
                try:
                    self.play_area.addch(y, x, 'x')
                except BaseException:
                    pass
        self.stdscr.refresh()

    def run(self):
        counter = 0
        try:
            self.setup_curses()
            self.reset_all()
            while True:
                ch = self.stdscr.getch()
                match ch:
                    case -1:
                        self.stdscr.addstr(self.maxy // 2,
                            self.maxx // 2, f"{counter}")
                        counter += 1
                    case other:
                        return
        except BaseException as e:
            print(e)
        finally:
            self.teardown_curses()