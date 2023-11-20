from enum import Enum
import pyautogui
import time
import datetime


class RingTimer(Enum):
    roh = 480
    life_ring = 1200


class Ring:
    def __init__(self, ring_type, last_swapped=None, swap_rings=False) -> None:
        self.last_swapped = last_swapped
        self.swap_rings = swap_rings
        self.rings_available = True
        self.ring_type = ring_type

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
