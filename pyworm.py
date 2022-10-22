#!/usr/bin/env python3

import wormcurses
import wormstate

if __name__ == "__main__":
    # Start the curses user interface
    worm_interface = wormcurses.WormCurses()

    # Create the game state and pass it to the interface
    worm_interface.set_state(wormstate.WormState())

    # Start the game loop
    worm_interface.run()

    print("Bye!")