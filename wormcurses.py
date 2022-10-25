import curses
import random
import time
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
                    Status: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
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
keys.KEY_n = ord('n')
keys.KEY_N = ord('N')
keys.KEY_p = ord('p')
keys.KEY_P = ord('P')
keys.KEY_q = ord('q')
keys.KEY_Q = ord('Q')
keys.KEY_CTRL_L = ord('L') - 64
# Curses doesn't define shifted up or down keys for some reason
# And these don't work in a MacOS standard terminal. They do work in the
# VSCode terminal. Sigh.
keys.KEY_SDOWN = 336
keys.KEY_SUP = 337

# Every time the worm eats a number it says a random phrase from this list
worm_quotes = [
    "Yum!", "Delicious!", "I want MORE!", "Tasty!", "I'm still hungry!",
    "Keep feeding me!", "I can't get enough!",
    "Does this screen make me look fat?", "You spoil me!",
    "My compliments to the chef!"
]
worm_max_quote = len(worm_quotes) - 1

class WormCurses(object):
    """
    A curses user interface for the game of worm
    """
    def set_state(self, state: wormstate.WormState):
        self.state = state
        self.prng = random.Random(time.time())

    def setup_curses(self):
        """
        Setup all features of curses we want for this application.
        """
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.timeout(1000)

    def teardown_curses(self):
        """
        Return the terminal to the pre-curses state. If this doesn't get
        called the user should be able to type 'stty sane' to reset the
        terminal.
        """
        self.stdscr.keypad(False)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def draw_static_content(self):
        """
        Draw all of the content that shouldn't change at all during the game
        """
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
        """
        Wraps the curses addch method which will throw an exception when
        writing to the lower right corner of the screen
        """
        try:
            self.play_area.addch(y, x, c)
        except curses.error:
            pass

    def draw_target(self):
        """ Draw the random target number on the screen."""
        self.play_area.addch(self.state.target_y, self.state.target_x,
             str(self.state.target_value))

    def draw_grow_by(self):
        """ Draw the 'grow by' value on the screen."""
        self.stdscr.addstr(0, 10, str(self.state.grow_count))

    def draw_score(self):
        """ Draw the score value on the screen. """
        self.stdscr.addstr(0, self.maxx - 5, str(self.state.score).ljust(4))

    def draw_worm_full(self):
        """ Draw the entire worm on the screen. """
        w = self.state.worm.left
        c = '@'
        while w != self.state.worm:
            self.safe_addch(w.y, w.x, c)
            c = 'o'
            w = w.left

    def draw_worm_update(self, old_xy):
        """
        Efficiently animate a single step of the worm by only drawing the
        new head, overwriting the old head, and if necessary, erase the
        old tail.
        """
        w = self.state.worm.left
        self.safe_addch(w.y, w.x, '@')
        w = w.left
        if w != self.state.worm:
            self.safe_addch(w.y, w.x, 'o')
        if (old_xy != None):
            x, y = old_xy
            self.safe_addch(y, x, ' ')

    def draw_status(self):
        """ Draw the status line. """
        try:
            y = self.maxy - 1
            x = (self.maxx - len(self.status)) // 2
            self.stdscr.move(y, 0)
            self.stdscr.deleteln()
            self.stdscr.addstr(y, x, self.status)
        except curses.error:
            pass

    def next_step(self, n):
        """
        Advance the state of the game by n steps. If we hit a target number,
        the wall, or the worm, we stop advancing.
        """
        try:
            for i in range(n):
                (old_xy, status) = self.state.next_step()
                if status != None:
                    if old_xy != None:
                        (x, y) = old_xy
                        x = max(x, 0)
                        y = max(y, 0)
                        self.play_area.addch(y, x, 'X')
                    self.status = status + ": Hit 'N' for new game or Q to quit"
                    self.draw_status()
                    return
                else:
                    self.draw_target()
                    self.draw_worm_update(old_xy)
                    self.draw_grow_by()
                    self.draw_score()
                    self.draw_status()
                    self.counter += 1
                    if self.old_grow_count < self.state.grow_count:
                        self.status = worm_quotes[self.prng.randint(0, worm_max_quote)]
                        return
        finally:
            self.old_grow_count = self.state.grow_count
            self.play_area.refresh()
            self.stdscr.refresh()

    def draw_all(self):
        """ Redraw everything on the screen (completely refresh). """
        self.draw_static_content()
        self.draw_grow_by()
        self.draw_score()
        self.draw_status()
        self.stdscr.refresh()
        self.draw_target()
        self.draw_worm_full()
        self.play_area.refresh()

    def reset_all(self):
        """ Reset all state to start a new game. """
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

        # No status to report
        self.status = ""

        # Remember the grow count so we can tell whenever it increases
        self.old_grow_count = self.state.grow_count

        # Draw everything
        self.draw_all()

    def run(self):
        """ Main game loop. """
        self.counter = 0
        self.paused = False
        try:
            self.setup_curses()
            self.reset_all()
            while True:
                ch = self.stdscr.getch()
                if self.state.game_over:
                    match ch:
                        case keys.KEY_n | keys.KEY_N:
                            self.reset_all()
                        case keys.KEY_q | keys.KEY_Q:
                            return
                        case curses.KEY_RESIZE:
                            self.reset_all()
                            continue
                        case _:
                            continue
                elif self.paused:
                    match ch:
                        case keys.KEY_p | keys.KEY_P:
                            self.status = ""
                            self.paused = False
                            self.draw_status()
                            self.stdscr.refresh()
                        case keys.KEY_q | keys.KEY_Q:
                            return
                        case curses.KEY_RESIZE:
                            self.reset_all()
                            continue
                        case _:
                            continue
                else:
                    match ch:
                        case keys.TIMEOUT:
                            self.next_step(1)
                        case keys.KEY_h | curses.KEY_LEFT:
                            self.state.go_left()
                            self.next_step(1)
                        case keys.KEY_j | curses.KEY_DOWN:
                            self.state.go_down()
                            self.next_step(1)
                        case keys.KEY_k | curses.KEY_UP:
                            self.state.go_up()
                            self.next_step(1)
                        case keys.KEY_l | curses.KEY_RIGHT:
                            self.state.go_right()
                            self.next_step(1)
                        case keys.KEY_H | curses.KEY_SLEFT:
                            self.state.go_left()
                            self.next_step(5)
                        case keys.KEY_J | keys.KEY_SDOWN: # special case
                            self.state.go_down()
                            self.next_step(5)
                        case keys.KEY_K | keys.KEY_SUP: # special case
                            self.state.go_up()
                            self.next_step(5)
                        case keys.KEY_L | curses.KEY_SRIGHT:
                            self.state.go_right()
                            self.next_step(5)
                        case keys.KEY_CTRL_L | curses.KEY_REFRESH:
                            self.draw_all()
                        case keys.KEY_q | keys.KEY_Q:
                            return
                        case keys.KEY_p | keys.KEY_P:
                            self.status = "Paused: Hit P to continue"
                            self.draw_status()
                            self.stdscr.refresh()
                            self.paused = True
                        case curses.KEY_RESIZE:
                            self.reset_all()
                            continue
                        case _:
                            pass
        finally:
            self.teardown_curses()