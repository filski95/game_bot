import time
from random import randint, shuffle, uniform
import keyboard
import pyautogui
from PIL import Image
from sys import platform
import requests  # type: ignore
import datetime
import logging
from typing import Union
import os
from dotenv import load_dotenv

load_dotenv()

username = os.environ.get("medivia-username")
password = os.environ.get("medivia-password")


def return_system_divider():
    if platform == "win32":
        return 1
    else:
        return 2


class ApiCall:
    def __init__(self, last_call_ts=None, cached_for=60) -> None:
        self.last_call_ts: Union[int, None] = last_call_ts
        self.players: list = []  # to return in case we are still within cache period
        self.cached_for = cached_for

    def call_api_online_players(self, world):
        if self.check_if_cache_expired():
            req = requests.get(f"https://medivia.online/api/public/online/{world}", auth=(username, password))
            json_resp = req.json()
            cached_at, cached_for, players = json_resp["cached_at"], json_resp["cached_for"], json_resp["players"]
            self.last_call_ts, self.cached_for = cached_at, cached_for  # save the newest cached_at timestamp
            return cached_at, players, True
        else:
            return self.last_call_ts, self.players, False

    def check_if_cache_expired(self):
        current_timestamp = round(datetime.datetime.now().timestamp(), None)

        if self.last_call_ts is not None:
            # return false for 0-59 seconds
            if current_timestamp - self.last_call_ts < self.cached_for:
                return False
        return True


class Bot:
    is_hungry: bool = True
    mana = (26, 26, 26)
    hotkey = "F9"
    bot_on = True
    win_or_mac = return_system_divider()
    ctrl = (lambda divider: "ctrl" if divider == 1 else "cmd")(win_or_mac)
    world = "Pendulum"
    blacklist = {"Medivioo"}
    api_call = ApiCall()

    def __init__(self):
        self.food = self.find_food()  # find mushrooms and remember its position on the screen

    def run_bot(self):
        pyautogui.FAILSAFE = True

        while self.bot_on is True:
            self.check_if_hungry()
            self.anti_afk()
            self.use_up_mana()
            self.check_blacklist()

    def turn_bot_off_and_log(self, nick):
        self.bot_on = False

        self.logout()
        logging.basicConfig(
            filename="my_log_file.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info(f"{nick} has logged on - bot turned off")

    def check_blacklist(self):
        cached_at, players, new_data = self.api_call.call_api_online_players(self.world)

        if new_data:
            for player in players:
                nick = player["name"]
                if nick in self.blacklist:
                    self.turn_bot_off_and_log(nick)
                    print(datetime.datetime.fromtimestamp(cached_at))

    def find_food(self):
        food = pyautogui.locateOnScreen("ss/mushrooms.png", confidence=0.8)

        return food

    def check_if_hungry(self):
        """
        check if hungry, if so then make sure food location is available (could be that one stack was eaten so we need to find another one)
        """
        hungry_location = pyautogui.locateCenterOnScreen("ss/hungry.png")

        if hungry_location:
            self.food = self.find_food()
            self._eat_food()
        else:
            return False

        return False

    def _eat_food(self):
        left, top = self.food.left / self.win_or_mac, self.food.top / self.win_or_mac

        pyautogui.moveTo(left, top)
        pyautogui.doubleClick(button="right")
        time.sleep(0.25)
        pyautogui.click(button="right")
        time.sleep(0.25)
        pyautogui.click(button="right")
        print("eating food")

    def _press_cmd_and_key(self, key):
        rng = uniform(0.10, 0.12)
        keyboard.press("ctrl")
        pyautogui.press(key)
        time.sleep(rng)
        keyboard.release("ctrl")
        time.sleep(rng)

    def anti_afk(self):
        "anti afk movements + rng element to make char moves rarely"

        arrow_keys = ["left", "right", "up", "down"]
        rng_move = randint(1, 1000)

        # rng_move = 1
        if rng_move == 1:
            time.sleep(1)
            self._press_cmd_and_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_key(arrow_keys[0])

        print(rng_move)

    def _check_if_mana_full(self):
        mana = pyautogui.screenshot("ss/ss_mana.png", region=(2531, 118, 1, 1))
        pix = pyautogui.pixel(2531 * self.win_or_mac, 118 * self.win_or_mac)

        if pix != self.mana:
            print(pix)
            # pyautogui.moveTo(1411, 148)
            # time.sleep(100)
            return True
        else:
            return False

    def use_up_mana(self):
        # 1411, 148 -> mana bar must be in the top right corner

        mana_full = self._check_if_mana_full()
        if mana_full:
            for i in range(10):
                keyboard.press_and_release(self.hotkey)
                time.sleep(0.5)

    def logout(self):
        """log out"""
        keyboard.press("ctrl")
        keyboard.press("q")
        time.sleep(0.5)
        keyboard.release("ctrl")
        print("bot turned off")
        time.sleep(0.1)
        self.bot_on = False


if __name__ == "__main__":
    bot = Bot()
    time.sleep(2)
    bot.run_bot()
    # while True:
    #     time.sleep(2)
    #     x, y = pyautogui.position()
    #     print(x, y)
    #     print(pyautogui.pixel(x, y))
