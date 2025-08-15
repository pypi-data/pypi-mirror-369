"""PyHangouts2: A Selenium-based Google Chat library."""

# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from warnings import warn
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import bs4

__version__ = "1.1.0"


class PyHangouts2:
    def __init__(self, headless=False):
        self.options = webdriver.ChromeOptions()
        if headless:
            warn("Headless mode may not work properly.", FutureWarning)
            self.options.add_argument("--headless=new")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.minimize_window()
        self.is_in_space = False
        self.is_logged_in = False
        self.space = None

    def login(self, method="manual", username=None, password=None):
        """Log in"""
        if self.is_logged_in:
            raise StatusError("User is already logged in")
        self.driver.maximize_window()
        if method == "auto":
            warn("Automatic login may not work properly.", FutureWarning)
            if not username or not password:
                raise AuthorizationError("Authentication info not completely provided.")
            self.driver.get("https://mail.google.com/chat/u/0/#chat/home")
            actions = ActionChains(self.driver)
            actions.send_keys(username).send_keys(Keys.ENTER).perform()
            time.sleep(3)
            actions.send_keys(password).send_keys(Keys.ENTER).perform()
            WebDriverWait(self.driver, 60).until(
                EC.url_matches("https://mail.google.com/chat/u/0/#chat/home")
            )
        elif method == "manual":
            self.driver.get("https://mail.google.com/chat/u/0/#chat/home")
            WebDriverWait(self.driver, 60).until(
                EC.url_matches("https://mail.google.com/chat/u/0/#chat/home")
            )
        else:
            raise SyntaxError("No valid login method provided!")
        self.driver.minimize_window()
        self.is_logged_in = True

    def join(self, space):
        """Join space"""
        if not self.is_logged_in:
            raise StatusError("User is not logged in")
        space_url = f"https://mail.google.com/chat/u/0/#chat/{space}"
        self.driver.get(space_url)
        WebDriverWait(self.driver, 60).until(EC.url_matches(space_url))
        self.driver.switch_to.frame(
            self.driver.find_element(by=By.NAME, value="single_full_screen")
        )
        time.sleep(1)
        self.is_in_space = True
        self.space = space

    def leave(self):
        """Leave space"""
        if not self.is_in_space:
            raise StatusError("User is not logged in")
        self.driver.switch_to.default_content()
        self.driver.get("https://mail.google.com/chat/u/0/#chat/home")
        WebDriverWait(self.driver, 60).until(
            EC.url_matches("https://mail.google.com/chat/u/0/#chat/home")
        )
        self.is_in_space = False
        self.space = None

    def ls(self):
        """List DMs and spaces"""
        if self.is_in_space:
            raise StatusError("User is in a space")
        self.driver.switch_to.frame(
            self.driver.find_element(by=By.NAME, value="single_full_screen")
        )
        page_html = self.driver.page_source
        soup = bs4.BeautifulSoup(page_html, "lxml")
        spaces = []
        spacesget = soup.find(
            "div",
            attrs={
                "jsname": "WbL0Ac",
                "role": "list",
                "aria-labelledby": "EWK8Bb-tJHJj",
                "jsaction": "UEEsmf:xO5IE;",
            },
        )
        for i in spacesget.contents:
            spaceid = i.attrs["id"].replace("/SCcFR", "")
            spaceattrs = (
                i.find("div")
                .find("div")
                .find(lambda tag: tag.name == "div" and "jsname" not in tag.attrs)
                .find("div", class_="Tcg1Uc")
                .find("div", class_="zeiL7e")
            )
            spacename = (
                spaceattrs.find("div", class_="WcXjib")
                .find("div", class_="Vb5pDe")
                .string
            )
            spacemsgs = spaceattrs.find("div", class_="ERFjwe").find(
                lambda tag: tag.name == "span" and "Hkj4n" in tag.attrs["class"]
            )
            spacemsg = ""
            spacemsgauthor = ""
            for msg in spacemsgs.contents:
                if isinstance(msg, bs4.element.Tag):
                    spacemsgauthor = msg.string
                    if spacemsgauthor:
                        spacemsgauthor = spacemsgauthor.strip()[:-1]
                if isinstance(msg, bs4.element.NavigableString):
                    spacemsg = msg
            if not spacemsgauthor:
                # in a dm, if other person sends message it doesn't show author
                spacemsgauthor = spacename
            spacemessage = Message(spacemsgauthor, spacemsg)
            spaces.append(Space(spaceid, spacename, spacemessage))
        self.driver.switch_to.default_content()
        return spaces

    def chat(self, message):
        """Send a message in a space"""
        if not self.is_in_space:
            raise StatusError("User is not in a space")
        typeui = self.driver.find_element(
            by=By.XPATH,
            value='//div[@jsname="yrriRe"]',
        )
        typeui.send_keys(message)
        typeui.send_keys(Keys.RETURN)

    def get_current_msg(self):
        """
        Gets the latest message in the space and outputs a Message object.
        This function is a bit buggy, but it works most of the time.
        If you want to have guaranteed accuracy, use the `ls` function.
        I may in fact deprecate this function in the future, but it's here for now.
        """
        if not self.is_in_space:
            raise StatusError("User is not in a space")
        page_html = self.driver.page_source
        soup = bs4.BeautifulSoup(page_html, "lxml")
        currentmsg = ""
        # todo: replies don't work
        try:
            for i in (
                soup.find_all(class_="rogmqd")[-1]
                .find("div", class_="DTp27d QIJiHb Zc1Emd")
                .contents
            ):
                if isinstance(i, bs4.element.NavigableString):
                    currentmsg += i
                if isinstance(i, bs4.element.Tag):
                    if i.name == "img":
                        if i.attrs.get("alt"):
                            currentmsg += i.attrs["alt"]
                    if i.name in ('b', 'i'):
                        if i.string:
                            currentmsg += i.string
        except (
            AttributeError
        ) as e:  # AttributeError: 'NoneType' object has no attribute 'contents'
            # this error happens when user sends ONLY image/file
            raise NoMessageFoundError("No messages found.") from e
        currentauthor = (
            soup.find_all(class_="nzVtF")[-1].find("span").find("span").string
        )
        if currentmsg and currentauthor:
            return Message(author=currentauthor, message=currentmsg)
        raise NoMessageFoundError("No messages found.")

    def list_messages(self):
        """Probably worse than `get_current_msg`"""
        if not self.is_in_space:
            raise StatusError("User is not in a space")
        page_html = self.driver.page_source
        soup = bs4.BeautifulSoup(page_html, "lxml")
        divs = soup.find_all("div", class_="F0wyae oGsu4")
        for div in divs:
            msg = ""
            nosend = False
            auth = div.find("span", class_="nzVtF").find("span").find("span").string
            # msg = (
            #     div.find("div", class_="rogmqd")
            #     .find("div", class_="DTp27d QIJiHb Zc1Emd")
            #     .string
            # )
            try:
                for i in (
                    div.find_all(class_="rogmqd")[-1]
                    .find("div", class_="DTp27d QIJiHb Zc1Emd")
                    .contents
                ):
                    if isinstance(i, bs4.element.NavigableString):
                        msg += i
                    if isinstance(i, bs4.element.Tag):
                        if i.name == "img":
                            if i.attrs.get("alt"):
                                msg += i.attrs["alt"]
                        if i.name in ('b', 'i'):
                            if i.string:
                                msg += i.string
            except (
                AttributeError
            ):  # AttributeError: 'NoneType' object has no attribute 'contents'
                # this error happens when user sends ONLY image/file
                nosend = True
            if not nosend:
                yield Message(author=auth, message=msg)

    def end(self):
        """Stops the driver and ends the session"""
        self.driver.quit()


class Message:
    def __init__(self, author, message):
        self.author = author
        self.message = message


class Space:
    def __init__(self, spaceid: str, name: str, message: Message):
        self.spaceid = spaceid
        self.name = name
        self.message = message


class StatusError(Exception):
    pass


class NoMessageFoundError(Exception):
    pass


class AuthorizationError(Exception):
    pass
