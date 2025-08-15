#!/usr/bin/env python3
"""Google Chat for Character.AI"""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import os
import pickle
import configparser
import time
import PyCharacterAI
import pyhangouts2

MODEL = input("Character? ")

WILL_REUSE = False

if os.path.exists("token.pkl"):
    WILL_REUSE = input("Reuse token? (y/N) ") == "y"

if WILL_REUSE:
    with open("token.pkl", "rb") as a:
        TOKEN = pickle.load(a)
else:
    TOKEN = input("Token? ")
    with open("token.pkl", "wb") as b:
        pickle.dump(TOKEN, b)

config = configparser.ConfigParser()

config.read("config.ini")

login_config = dict(dict(config).get("login", {}))

hangouts = pyhangouts2.PyHangouts2()

spacename = input('Space? (ex. "dm/XXXXXXXXXXX" or "space/XXXXXXXXXXX") ')

hangouts.login(
    login_config.get("method", "manual"),
    login_config.get("username"),
    login_config.get("password"),
)

hangouts.join(spacename)


async def characterai_chat(message: str, chat_id, character_id):
    client = await PyCharacterAI.get_client(token=TOKEN)
    me = await client.account.fetch_me()
    print(f"Authenticated as @{me.username}")
    airesponse = await client.chat.send_message(character_id, chat_id, message)
    aicontent = " ".join(airesponse.get_primary_candidate().text.split())
    with open("response.pkl", "wb") as c:
        pickle.dump(aicontent, c)
    await client.close_session()


async def begin_chat():
    client = await PyCharacterAI.get_client(token=TOKEN)
    me = await client.account.fetch_me()
    print(f"Authenticated as @{me.username}")
    chat, greeting_message = await client.chat.create_chat(MODEL)
    with open("chat.pkl", "wb") as d:
        pickle.dump({"chat": chat, "greeting_message": greeting_message}, d)
    await client.close_session()


asyncio.run(begin_chat())

with open("chat.pkl", "rb") as e:
    chatpkl = pickle.load(e)
cai_chat = chatpkl["chat"]
cai_greeting_message = chatpkl["greeting_message"]

old_message = ""
current_message = ""
author = ""

hangouts.chat(cai_greeting_message.get_primary_candidate().text)

time.sleep(3)

while True:
    try:
        currentmsg = hangouts.get_current_msg()

        current_message = currentmsg.message
        author = currentmsg.author

    except pyhangouts2.NoMessageFoundError:
        current_message = ""
        author = "You"

    # print("msgheader")
    # print(current_message)
    # print(old_message)
    # print(author)

    if current_message not in (old_message, "") and author != "You":
        sentmessage = f"{author}: {current_message}"
        # print(f"respond to {current_message}")
        asyncio.run(characterai_chat(sentmessage, cai_chat.chat_id, MODEL))
        with open("response.pkl", "rb") as f:
            response = pickle.load(f)
        hangouts.chat(response)
        ai_message = response
        old_message = current_message
