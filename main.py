from fishing import thais, fish_spots_abukir_eschen_slookey
from multiprocessing import Process, Manager
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
from enum import Enum
from fishing import Fishing
from ring import Ring
from api import ApiCall
from settings import Settings

load_dotenv()

username = os.environ.get("medivia-username")
password = os.environ.get("medivia-password")


def return_system_divider():
    if platform == "win32":
        return 1
    else:
        return 2


class Bot:
    is_hungry: bool = True
    mana = (26, 26, 26)
    hotkey = "F9"
    bot_on = True
    win_or_mac = return_system_divider()
    ctrl = (lambda divider: "ctrl" if divider == 1 else "cmd")(win_or_mac)
    blacklist = {"ASDASD Placeholder"}
    runes_made_at = 0  # timestamp

    def __init__(self, settings, should_run):
        self.food = self.find_food()
        self.settings = settings
        self.should_run = should_run
        self.started_at = round(datetime.datetime.now().timestamp(), None)
        self.fishing = Fishing(self.settings.fishing_cords)
        self.api_call = ApiCall(username, password)
        self.ring_swap = Ring("life_ring", swap_rings=True)

        print(f"caling {self.started_at}")

    def check_if_timeout(self):
        if self.settings.run_for is None:
            return True

        current = round(datetime.datetime.now().timestamp(), None)

        print(current - self.started_at)
        if current - self.started_at > self.settings.run_for:
            return False
        return True

    def run_rune_maker_and_fish(self):
        pyautogui.FAILSAFE = True

        while self.bot_on is True:
            if not self.check_if_timeout():
                self.should_run["run"] = False
                return False
            if self.ring_swap.swap_rings:
                self.check_ring_need()
            self.check_if_hungry()
            self.anti_afk()
            self.use_up_mana()

            if self.settings.run_fishing is True:
                good_to_fish = self.check_blacklist()

                if good_to_fish:
                    continue_running = self.run_fishing_V2(self.check_if_hungry)
                    if not continue_running:
                        return False

        # while self.bot_on is False:
        #     self.log_back_in_and_start_bot_if_possible()

    def run_fishing_V2(self, check_if_hungry):
        # * implementation tested along runemaking
        current = round(datetime.datetime.now().timestamp(), None)

        if (
            self.fishing.fishing_done_at is not None
            and current - self.fishing.fishing_done_at < self.settings.fishin_break
        ):
            pass
        else:
            run = self.fishing.use_fishing_rod(self.should_run)

            if not run:
                self.turn_bot_off_and_log("Swtichbladez")
                return False

            self.fishing.fishing_done_at = round(
                datetime.datetime.now().timestamp(), None
            )
        return True

    def run_fishing(self):
        pyautogui.FAILSAFE = True
        while self.bot_on is True:
            time.sleep(uniform(0.30, 0.50))
            self.fishing.use_fishing_rod()

    def check_ring_need(self):
        if not self.ring_swap.rings_available or not self.ring_swap.check_ring_time:
            return False

        self.ring_swap.swap_ring_procedure()

    def log_back_in_and_start_bot_if_possible(self):
        if not self.check_api_if_danger_persist():
            time.sleep(randint(300, 600))
            self.log_back_on_and_continue()

    def log_back_on_and_continue(self):
        self.bot_on = True
        keyboard.press_and_release("enter")
        self.run_rune_maker()

    def check_api_if_danger_persist(self):
        cached_at, players, new_data = self.api_call.call_api_online_players()

        online_blacklist_players_count = 0

        if new_data:
            for player in players:
                nick = player["name"]
                if nick in self.blacklist:
                    online_blacklist_players_count += 1

            if online_blacklist_players_count == 0:
                return False
            else:
                return True

    def turn_bot_off_and_log(self, nick):
        if self.settings.key_to_safety is not None:
            pyautogui.press(self.settings.key_to_safety)
            time.sleep(randint(1, 10))
        self.bot_on = False
        print("bot turned off")

        self.logout()
        logging.basicConfig(
            filename="my_log_file.log",
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logging.info(f"{nick} has logged on - bot turned off")

    def check_blacklist(self):
        cached_at, players, new_data = self.api_call.call_api_online_players()

        if new_data:
            for player in players:
                nick = player["name"]
                if nick in self.blacklist:
                    self.turn_bot_off_and_log(nick)
                    print(datetime.datetime.fromtimestamp(cached_at))
                    self.should_run["run"] = False
                    return False
        return True

    def find_food(self):
        food = pyautogui.locateCenterOnScreen("ss/fish.png", confidence=0.8)
        if food is None:
            food = pyautogui.locateCenterOnScreen("ss/mushrooms.png")

        return food

    def check_if_hungry(self):
        """
        check if hungry, if so then make sure food location is available (could be that one stack was eaten so we need to find another one)
        """
        hungry_location = pyautogui.locateCenterOnScreen(
            "ss/hungry.png", confidence=0.8
        )

        if hungry_location:
            self.food = self.find_food()
            self._eat_food()
        else:
            return False

        return False

    def _eat_food(self):
        print("eating")

        pyautogui.moveTo(self.food.x / self.win_or_mac, self.food.y / self.win_or_mac)

        for i in range(8):
            time.sleep(0.25)
            print("eating food")
            pyautogui.click(button="right")
            time.sleep(0.25)

    def _press_cmd_and_key(self, key):
        rng = uniform(0.10, 0.12)
        if self.win_or_mac == 1:
            keyboard.press(self.ctrl)
            pyautogui.press(key)
            time.sleep(rng)
            keyboard.release(self.ctrl)
            time.sleep(rng)
        else:
            pyautogui.keyDown(self.ctrl)
            pyautogui.press(key)
            time.sleep(rng)
            pyautogui.keyUp("self.ctrl")
            time.sleep(rng)

    def anti_afk(self):
        "anti afk movements + rng element to make char moves rarely"

        arrow_keys = ["left", "right", "up", "down"]
        rng_move = randint(1, self.settings.anti_afk_frequency)

        # rng_move = 1
        if rng_move == 1:
            time.sleep(1)
            self._press_cmd_and_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_key(self.settings.last_key_anti_afk)

        print(rng_move)

    def _check_if_mana_full(self):
        current_time = round(datetime.datetime.now().timestamp(), None)

        if current_time - self.runes_made_at < 500:
            return False

        #  mana = pyautogui.screenshot("ss/ss_mana.png", region=(1411, 148, 1, 1)) # MAC
        mana = pyautogui.screenshot("ss/ss_mana.png", region=(2520, 98, 1, 1))
        pix = pyautogui.pixel(2520 * self.win_or_mac, 98 * self.win_or_mac)

        if pix != self.mana:
            # pyautogui.moveTo(1411, 148)
            # time.sleep(100)
            return current_time  # returnning timestamp which will evaluate to true + be assigned to runes_made_at variable
        else:
            return False

    def use_up_mana(self):
        # 1411, 148 -> mana bar must be in the top right corner

        mana_full = self._check_if_mana_full()
        if mana_full:
            for i in range(5):
                keyboard.press_and_release(self.hotkey)
                time.sleep(1)

        self.runes_made_at = mana_full

    def logout(self):
        """log out - for some reason pyautogui functions did not work with "q" """
        keyboard.press(self.ctrl)
        keyboard.press("q")
        time.sleep(0.5)
        keyboard.release(self.ctrl)

        time.sleep(0.1)
        self.bot_on = False

    def check_dangerous_player_vip(self, player):
        player_vip = pyautogui.locateOnScreen(f"ss/{player}.png", confidence=0.8)

        print("running check")
        if player_vip:
            print("found player in Vip!")
            self.should_run["run"] = False
            self.turn_bot_off_and_log(f"{player}")

            return True
        return False

    def check_vip(self):
        # * dangerous player must correspond to a png screenshot.
        dangerous_players = ["Switchbladez"]

        while self.should_run["run"] is True:
            for player in dangerous_players:
                found = self.check_dangerous_player_vip(player)
                if found:
                    return found


if __name__ == "__main__":
    settings_EK_Abukir2 = Settings(
        "EK_Abukir2_with_fishing",
        6,
        "up",
        "down",
        100,
        True,
        30,
        None,
        thais,
    )

    settings_ED_Domek = Settings(
        "EK_Abukir2_with_fishing",
        6,
        "up",
        "down",
        400,
        False,
        30,
        None,
        thais,
    )

    time.sleep(2)

    with Manager() as bot_manager:
        should_run = bot_manager.dict()
        should_run["run"] = True
        bot = Bot(settings=settings_ED_Domek, should_run=should_run)
        main_process = Process(target=bot.run_rune_maker_and_fish)
        # vip_process = Process(target=bot.check_vip, args=(should_run,))

        main_process.start()
        # vip_process.start()
        main_process.join()
    # vip_process.join()

    # vip_process.terminate()
    # vip_process.join()
    # main_process.terminate()
    # main_process.join()d

    # bot.run_fishing()a
    # pyautogui.moveTo(1154, 582)
    # l = []
    # ctr = 1
    # while True:
    #     time.sleep(1)
    #     x, y = pyautogui.position()
    #     l.append([x, y])
    #     print(x, y)
    #     ctr += 1
    #     if ctr % 10 == 0:
    #         print(l)
    # while True:
    # time.sleep(2)
    # pyautogui.moveTo(2520, 98)
    # x, y = pyautogui.position()
    # print(x, y)
    # print(pyautogui.pixel(x, y))
