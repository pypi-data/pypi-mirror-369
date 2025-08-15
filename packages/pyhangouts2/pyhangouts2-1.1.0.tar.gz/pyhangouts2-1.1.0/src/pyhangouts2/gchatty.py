#!/usr/bin/env python3
"""G-ChaTTY: A CLI for Google Chat."""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import curses
import argparse
import os
from configparser import ConfigParser
import threading
import time
import pyhangouts2.selectoptions as so
import pyhangouts2

stop_threads = False

if __name__ != "__main__":
    raise RuntimeError("This file is not meant to be imported.")


def parse_args():
    parser = argparse.ArgumentParser(description="G-ChaTTY")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode?")
    parser.add_argument(
        "-s", "--space", type=str, help="Space to automatically join.", default=None
    )
    parser.add_argument(
        "-c", "--config", type=str, help="Config file to use.", default="config.ini"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"G-ChaTTY {pyhangouts2.__version__}",
    )
    args = parser.parse_args()
    return args


arguments = parse_args()

hangouts = pyhangouts2.PyHangouts2(headless=arguments.headless)

config = ConfigParser()

login_config = {}

# check if config exists
if os.path.exists(arguments.config):
    config.read(arguments.config)

    login_config = dict(dict(config).get("login", {}))

hangouts.login(
    login_config.get("method", "manual"),
    login_config.get("username"),
    login_config.get("password"),
)


def select_space():
    spaces = hangouts.ls()

    spacesrender = []
    spacesselect = []

    for space in spaces:
        spacesrender.append(
            f"{space.name} ({space.message.author}: {space.message.message})"
        )
        spacesselect.append(space.spaceid)

    spacesrender.append("Exit")
    spacesselect.append("Exit")

    so.update_options(spacesrender)
    so.real_options(spacesselect)

    to_join = curses.wrapper(so.select)

    hangouts.join(to_join)

    # clear screen
    print("\033[H\033[J", end="")


class stdout_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Welcome to G-ChaTTY. Type /? for help.")
        old_message = ""
        current_message = ""
        author = ""

        for i in hangouts.list_messages():
            print(f"{i.author}: {i.message}")
            old_message = i.message

        while True:
            if stop_threads:
                break
            try:
                currentmsg = hangouts.get_current_msg()

                current_message = currentmsg.message
                author = currentmsg.author

            except pyhangouts2.NoMessageFoundError:
                current_message = ""
                author = "You"

            if current_message not in (old_message, ""):
                sentmessage = f"{author}: {current_message}"
                print(sentmessage)
                old_message = current_message


if __name__ == "__main__":
    if arguments.space:
        hangouts.join(arguments.space)
    else:
        select_space()

    out_thread = stdout_thread()

    out_thread.start()

    while True:
        to_chat = input()
        if to_chat == "/back":
            stop_threads = True
            out_thread.join()
            hangouts.leave()
            time.sleep(1)
            select_space()
            # restart
            stop_threads = False
            out_thread = stdout_thread()
            out_thread.start()
            to_chat = ""
        if to_chat == "/exit":
            stop_threads = True
            out_thread.join()
            hangouts.end()
            break
        if to_chat in ('/?', '/help'):
            print("Commands:")
            print("/exit - Exit")
            print("/back - Back to space selection")
            print("/? - Help")
            to_chat = ""
        hangouts.chat(to_chat)
