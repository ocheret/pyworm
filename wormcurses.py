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

    def draw_worm_full(self):
        w = self.state.worm.left
        c = '@'
        while w != self.state.worm:
            x, y = w.value
            self.play_area.addch(y, x, c)
            c = 'o'
            w = w.left

    def draw_worm_update(self, old_xy):
        w = self.state.worm.left
        x, y = w.value
        self.play_area.addch(y, x, '@')
        w = w.left
        if w != self.state.worm:
            x, y = w.value
            self.play_area.addch(y, x, 'o')
        if (old_xy != None):
            x, y = old_xy
            self.play_area.addch(y, x, ' ')

    def draw_status(self, status):
        try:
            y = self.maxy - 1
            x = (self.maxx - len(status)) // 2
            self.stdscr.move(y, 0)
            self.stdscr.deleteln()
            self.stdscr.addstr(y, x, status)
        except curses.error:
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
        self.play_maxx = self.maxx - 2  # account for border on both sides
        self.play_maxy = self.maxy - 4  # account for border, header, and footer
        self.state.reset(width = self.maxx - 2, height = self.maxy - 4)
        # for x in range(self.state.width):
        #     for y in range(self.state.height):
        #         try:
        #             self.play_area.addch(y, x, curses.ACS_BULLET)
        #         except curses.error:
        #             pass
        self.draw_worm_full()
        self.stdscr.refresh()

    def next_step(self):
        old_xy = self.state.next_step()
        self.draw_worm_update(old_xy)
        self.draw_status(f"Iterations {self.counter}.")
        self.counter += 1
        self.play_area.refresh()
        self.stdscr.refresh()

    def run(self):
        self.counter = 0
        try:
            self.setup_curses()
            self.reset_all()
            while True:
                ch = self.stdscr.getch()
                if ch == ord('h') or ch == curses.KEY_LEFT:
                    self.state.go_left()
                    self.next_step()
                elif ch == ord('j') or ch == curses.KEY_DOWN:
                    self.state.go_down()
                    self.next_step()
                elif ch == ord('k') or ch == curses.KEY_UP:
                    self.state.go_up()
                    self.next_step()
                elif ch == ord('l') or ch == curses.KEY_RIGHT:
                    self.state.go_right()
                    self.next_step()
                elif ch == -1:
                    self.next_step()
                else:
                    return
        finally:
            self.teardown_curses()