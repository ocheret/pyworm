#!/usr/bin/env python3

import wormcurses
import wormstate

if __name__ == "__main__":
    worm_interface = wormcurses.WormCurses()
    worm_interface.set_state(wormstate.WormState())
    worm_interface.run()