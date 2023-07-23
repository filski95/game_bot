import time
from random import randint, shuffle, uniform

import pyautogui
from PIL import Image


class Bot:
    is_hungry: bool = True
    mana = (26, 26, 26)
    hotkey = "F12"

    def __init__(self):
        self.food = self.find_food()  # find mushrooms and remember its position on the screen

    def run_bot(self):
        pyautogui.FAILSAFE = True
        # time.sleep(3)
        self.check_if_hungry()
        self.anti_afk()
        self.use_up_mana()

    def find_food(self):
        food = pyautogui.locateOnScreen("ss/mushrooms.png")

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
        left, top = self.food.left / 2, self.food.top / 2

        pyautogui.moveTo(left, top)
        pyautogui.doubleClick(button="right")
        time.sleep(0.25)
        pyautogui.click(button="right")
        time.sleep(0.25)
        pyautogui.click(button="right")
        print("eating food")

    def _press_cmd_and_arrow_key(self, arrow_key):
        rng = uniform(0.20, 0.3)

        pyautogui.keyDown("command")
        pyautogui.press(arrow_key)
        time.sleep(rng)
        pyautogui.keyUp("command")
        time.sleep(rng)

    def anti_afk(self):
        "anti afk movements + rng element to make char moves rarely"

        arrow_keys = ["left", "right", "up", "down"]
        rng_move = randint(1, 400)

        if rng_move == 1:
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[0])

        elif rng_move == 2:
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[randint(0, 3)])
            self._press_cmd_and_arrow_key(arrow_keys[0])

        print(rng_move)

    def _check_if_mana_full(self):
        mana = pyautogui.screenshot("ss/ss_mana.png", region=(1411, 148, 1, 1))
        pix = pyautogui.pixel(1411 * 2, 148 * 2)

        if pix != self.mana:
            # print(pix)
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
                pyautogui.hotkey(self.hotkey)
                time.sleep(0.5)
        # implement functionality to use up mana


if __name__ == "__main__":
    bot = Bot()
    while True:
        time.sleep(2)

        bot.run_bot()
