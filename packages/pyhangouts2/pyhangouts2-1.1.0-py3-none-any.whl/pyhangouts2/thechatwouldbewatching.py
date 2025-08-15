#!/usr/bin/env python3
"""The chat WOULD be watching."""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
from configparser import ConfigParser
import json
import pyhangouts2

if __name__ != "__main__":
    raise RuntimeError("This file is not meant to be imported.")


def parse_args():
    parser = argparse.ArgumentParser(description="The chat WOULD be watching.")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode?")
    parser.add_argument(
        "-c", "--config", type=str, help="Config file to use.", default="config.ini"
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        help="Log file location",
        default="thechatwouldbewatching.log",
    )
    parser.add_argument(
        "-j",
        "--json",
        type=str,
        help="JSON file location",
        default="thechatwouldbewatching.json",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"thechatwouldbewatching {pyhangouts2.__version__}",
    )
    args = parser.parse_args()
    return args


def log(message, logfile, jsonfile):
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(
            f'[INFO] {message.name}: "{message.message.author}": {message.message.message}\n'
        )
    with open(jsonfile, "r", encoding="utf-8") as jr:
        jsonread = jr.read()
    with open(jsonfile, "w", encoding="utf-8") as j:
        js = json.loads(jsonread)
        js["log"].append(
            {
                "space": message.name,
                "message": message.message.message,
                "author": message.message.author,
            }
        )
        j.write(
            json.dumps(
                js,
                indent=4,
            )
        )


def inplus(message, no):
    for inp in no:
        if (
            f'{inp.name}: "{inp.message.author}": {inp.message.message}'
            == f'{message.name}: "{message.message.author}": {message.message.message}'
        ):
            return True


with open("thechatwouldbewatching.json", "w", encoding="utf-8") as j_init:
    j_init.write(
        json.dumps(
            {"log": []},
            indent=4,
        )
    )
with open("thechatwouldbewatching.log", "w", encoding="utf-8") as f_init:
    f_init.write("")

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

notwatching = hangouts.ls()

if __name__ == "__main__":
    while True:
        watching = hangouts.ls()
        for i in watching:
            if not inplus(i, notwatching):
                log(i, arguments.log, arguments.json)
        notwatching = watching
