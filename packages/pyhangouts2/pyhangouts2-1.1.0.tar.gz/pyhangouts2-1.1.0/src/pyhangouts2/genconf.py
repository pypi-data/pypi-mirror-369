#!/usr/bin/env python3
"""Generate config.ini"""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import sys

if __name__ != "__main__":
    raise RuntimeError("This file is not meant to be imported.")

if sys.argv[1] in ("-h", "--help"):
    print("Usage: python3 -m pyhangouts2.genconf [path (default: config.ini)]")
    sys.exit(0)

try:
    path = sys.argv[1]
except IndexError:
    path = "config.ini"

config = configparser.ConfigParser()

login_method = input("Login method? (auto/manual) ")
if login_method == "auto":
    config["login"] = {
        "method": "auto",
        "username": input("Username? "),
        "password": input("Password? "),
    }
elif login_method == "manual":
    config["login"] = {
        "method": "manual",
        "username": "",
        "password": "",
    }
else:
    raise SyntaxError("No valid login method provided!")

with open(path, "w", encoding="utf-8") as f:
    config.write(f)
