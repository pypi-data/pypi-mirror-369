"""Really bad code."""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import curses
import sys

if __name__ == "__main__":
    raise RuntimeError("This file is not meant to be executed.")
options = []
realoptions = []


def update_options(upd):
    global options
    options = upd


def real_options(upd):
    global realoptions
    realoptions = upd


def select(stdscr):
    # Clear screen
    stdscr.clear()

    # Define menu options
    current_row = 0

    while True:
        # Display the menu
        for idx, option in enumerate(options):
            if idx == current_row:
                stdscr.addstr(
                    idx, 0, option, curses.A_REVERSE
                )  # Highlight the current option
            else:
                stdscr.addstr(idx, 0, option)

        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        # Navigate the menu
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            break

    # Clear the screen before exiting
    stdscr.clear()
    stdscr.refresh()

    if realoptions[current_row] == "Exit":
        sys.exit()
    else:
        return realoptions[current_row]
