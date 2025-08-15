#!/usr/bin/env python3
"""Google Chat chatbot"""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import time
import ollama
import pyhangouts2

config = configparser.ConfigParser()

config.read("config.ini")

login_config = dict(dict(config).get("login", {}))

MODEL = input("Model? (default: llama3.1) ")

if MODEL == "":
    MODEL = "llama3.1"

hangouts = pyhangouts2.PyHangouts2()

spacename = input('Space? (ex. "dm/XXXXXXXXXXX" or "space/XXXXXXXXXXX") ')

hangouts.login(
    login_config.get("method", "manual"),
    login_config.get("username"),
    login_config.get("password"),
)

hangouts.join(spacename)


def ollama_chat(message: str, history: list):
    history.append({"role": "user", "content": message})
    airesponse = ollama.chat(model=MODEL, messages=history)
    aicontent = airesponse.message.content
    history.append({"role": "assistant", "content": aicontent})
    return aicontent, history


old_message = ""
current_message = ""
author = ""
aihistory = []

hangouts.chat("Hello World!")

time.sleep(3)

while True:
    try:
        currentmsg = hangouts.get_current_msg()

        current_message = currentmsg.message
        author = currentmsg.author
    except pyhangouts2.NoMessageFoundError:
        print("something broke")
        current_message = ""
        author = "You"

    # print("msgheader")
    # print(current_message)
    # print(old_message)
    # print(author)

    if current_message not in (old_message, "") and author != "You":
        sentmessage = f"{author}: {current_message}"
        print(f"respond to {current_message}")
        response, aihistory = ollama_chat(sentmessage, aihistory)
        hangouts.chat(response)
        ai_message = response
        old_message = current_message
