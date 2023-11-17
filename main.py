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
        self.world = "Pendulum"

    def call_api_online_players(self):
        if self.check_if_cache_expired():
            req = requests.get(
                f"https://medivia.online/api/public/online/{self.world}",
                auth=(username, password),
            )
            json_resp = req.json()
            cached_at, cached_for, players = (
                json_resp["cached_at"],
                json_resp["cached_for"],
                json_resp["players"],
            )
            self.last_call_ts, self.cached_for = (
                cached_at,
                cached_for,
            )  # save the newest cached_at timestamp
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


class RingTimer(Enum):
    roh = 480
    life_ring = 1200


class Ring:
    def __init__(self, last_swapped=None, swap_rings=False) -> None:
        self.last_swapped = last_swapped
        self.swap_rings = swap_rings
        self.rings_available = True
        self.ring_type = "roh"

    def swap_ring_procedure(self):
        if self.check_ring_time():
            ring_place = pyautogui.locateCenterOnScreen(
                "ss/ring_spot.png", confidence=0.90
            )

            if ring_place:
                self.move_ring_to_spot(ring_place)

    def move_ring_to_spot(self, ring_place):
        ring = pyautogui.locateCenterOnScreen(
            f"ss/{self.ring_type}.png", confidence=0.9
        )

        if not ring:
            self.rings_available = False
            return
        pyautogui.moveTo(ring)
        pyautogui.click()
        pyautogui.dragTo(ring_place, duration=1)
        self.last_swapped = round(datetime.datetime.now().timestamp(), None)
        time.sleep(1)

    def check_ring_time(self):
        time_to_expire = RingTimer[self.ring_type].value

        current_time = round(datetime.datetime.now().timestamp(), None)

        if self.last_swapped is None or (
            current_time - self.last_swapped > time_to_expire
        ):
            return True
        else:
            return False


class Fishing:
    def __init__(self) -> None:
        self.fishing_rod = self.find_fishing_rod()
        self.y_range = [120, 974]
        # self.x_range = [660, 1900]
        self.x_range = [660, 1200]
        self.city = "abukir"
        self.fish_spots = [
            [577, 1100],
            [583, 995],
            [587, 899],
            [585, 802],
            [577, 703],
            [583, 612],
            [587, 511],
            [578, 397],
            [589, 299],
            [582, 200],
            [595, 107],
            [680, 96],
            [664, 190],
            [670, 287],
            [663, 387],
            [664, 494],
            [673, 598],
            [684, 694],
            [672, 792],
            [662, 902],
            [683, 997],
            [673, 1083],
            [784, 1095],
            [770, 986],
            [770, 896],
            [771, 800],
            [770, 693],
            [775, 601],
            [776, 501],
            [770, 410],
            [771, 297],
            [774, 192],
            [782, 95],
            [881, 95],
            [874, 184],
            [871, 290],
            [875, 401],
            [869, 504],
            [868, 588],
            [874, 696],
            [877, 801],
            [871, 883],
            [875, 972],
            [877, 1096],
            [964, 1104],
            [962, 973],
            [962, 903],
            [980, 796],
            [979, 696],
            [977, 599],
            [969, 505],
            [980, 403],
            [980, 302],
            [989, 212],
            [987, 100],
            [1075, 98],
            [1074, 197],
            [1076, 302],
            [1088, 392],
            [1073, 497],
            [1073, 592],
            [1078, 699],
            [1080, 802],
            [1088, 907],
            [1083, 992],
            [1078, 1093],
            [1175, 1099],
            [1166, 994],
            [1168, 887],
            [1161, 798],
            [1276, 800],
            [1284, 905],
            [1273, 991],
            [1275, 1103],
            [1391, 1105],
            [1374, 1009],
            [1387, 883],
            [1378, 792],
            [1455, 793],
            [1463, 902],
            [1464, 997],
            [1468, 1086],
            [1569, 1085],
            [1573, 977],
            [1582, 900],
            [1579, 812],
            [1574, 711],
            [1575, 587],
            [1691, 590],
            [1682, 700],
            [1689, 804],
            [1693, 888],
            [1686, 990],
            [1676, 1097],
            [1767, 1096],
            [1784, 1004],
            [1790, 901],
            [1794, 794],
            [1788, 693],
            [1791, 601],
            [1897, 589],
            [1886, 698],
            [1895, 800],
            [1904, 890],
            [1885, 997],
            [1871, 1096],
            [1994, 1104],
            [1980, 986],
            [1983, 877],
            [1978, 792],
            [1985, 697],
            [1982, 592],
        ]

    def find_fishing_rod(self):
        fs = pyautogui.locateOnScreen("ss/fishing_rod.png", confidence=0.8)

        return fs

    def find_fishing_spots(self):
        # * work in progress
        sea = pyautogui.locateAllOnScreen(f"ss/sea_{self.city}.png", confidence=0.3)
        coords_range = []

        for spot in sea:
            coords_range.append(spot)

    def use_fishing_rod(self):
        print("fishing...")
        # x, y = self.get_spot_to_fish()
        for cords in self.fish_spots:
            x, y = cords
            time.sleep(0.2)
            pyautogui.moveTo(self.fishing_rod)
            time.sleep(0.10)
            pyautogui.click(button="right")
            time.sleep(0.15)
            pyautogui.moveTo(x, y)
            time.sleep(0.15)
            pyautogui.click(button="left")

    def get_spot_to_fish(self):
        x = randint(*self.x_range)
        y = randint(*self.y_range)

        return x, y


class Bot:
    is_hungry: bool = True
    mana = (26, 26, 26)
    hotkey = "F9"
    bot_on = True
    win_or_mac = return_system_divider()
    ctrl = (lambda divider: "ctrl" if divider == 1 else "cmd")(win_or_mac)
    blacklist = {"Medivioo", "Yeffo", "Queen Heal", "Ran Run", "Switchbladez"}
    key_to_safety = "down"
    api_call = ApiCall()
    fishing = Fishing()
    fishing_done_at = None
    ring_swap = Ring(swap_rings=True)
    runes_made_at = 0  # timestamp

    def __init__(self):
        self.food = (
            self.find_food()
        )  # find mushrooms and remember its position on the screen

    def run_rune_maker_and_fish(self):
        pyautogui.FAILSAFE = True

        while self.bot_on is True:
            if self.ring_swap.swap_rings:
                self.check_ring_need()
            self.check_if_hungry()
            self.anti_afk()
            self.use_up_mana()
            good_to_fish = self.check_blacklist()

            if good_to_fish:
                self.run_fishing_along_with_rune_making()

        # while self.bot_on is False:
        #     self.log_back_in_and_start_bot_if_possible()

    def run_fishing_along_with_rune_making(self):
        current = round(datetime.datetime.now().timestamp(), None)

        if self.fishing_done_at is not None and current - self.fishing_done_at < 15:
            pass
        else:
            run = self.fishing.use_fishing_rod(should_run)
            if not run:
                self.turn_bot_off_and_log
            self.fishing_done_at = round(datetime.datetime.now().timestamp(), None)

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
        if self.key_to_safety is not None:
            pyautogui.press(self.key_to_safety)
            time.sleep(randint(1, 10))
        self.bot_on = False

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
                    return False
        return True

    def find_food(self):
        food = pyautogui.locateOnScreen("ss/mushrooms.png")

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
        left, top = self.food.left * self.win_or_mac, self.food.top * self.win_or_mac

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
        rng_move = randint(1, 75)

        # rng_move = 1
        if rng_move == 1:
            time.sleep(1)
            self._press_cmd_and_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_key(arrow_keys[0])

        print(rng_move)

    def _check_if_mana_full(self):
        current_time = round(datetime.datetime.now().timestamp(), None)

        if current_time - self.runes_made_at < 500:
            return False

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
            for i in range(4):
                keyboard.press_and_release(self.hotkey)
                time.sleep(0.5)

        self.runes_made_at = mana_full

    def logout(self):
        """log out - for some reason pyautogui functions did not work with "q" """
        keyboard.press("ctrl")
        keyboard.press("q")
        time.sleep(0.5)
        keyboard.release("ctrl")

        time.sleep(0.1)
        self.bot_on = False

    def check_vip(self, should_run, pic="Slookey"):
        pass

        while True:
            player = pyautogui.locateOnScreen(f"ss/{pic}.png", confidence=0.8)

            if player:
                print("found Slookey!")
                self.turn_bot_off_and_log("Slookey - From Vip")
                return


if __name__ == "__main__":
    bot = Bot()
    time.sleep(2)

    with Manager() as bot_manager:
        should_run = bot_manager.dict()
        should_run["run"] = True

    main_process = Process(target=bot.run_rune_maker_and_fish)
    vip_process = Process(target=bot.check_vip, args=(should_run,))

    main_process.start()
    vip_process.start()

    # bot.run_fishing()
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
    #     time.sleep(1)
    #     pyautogui.moveTo(2520, 98)
    #     x, y = pyautogui.position()
    #     print(x, y)
    #     print(pyautogui.pixel(x, y))
