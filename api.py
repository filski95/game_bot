import datetime

from typing import Union

import requests


class ApiCall:
    def __init__(self, username, password, last_call_ts=None, cached_for=60) -> None:
        self.last_call_ts: Union[int, None] = last_call_ts
        self.players: list = []  # to return in case we are still within cache period
        self.cached_for = cached_for
        self.world = "Pendulum"
        self.username = username
        self.password = password

    def call_api_online_players(self):
        if self.check_if_cache_expired():
            req = requests.get(
                f"https://medivia.online/api/public/online/{self.world}",
                auth=(self.username, self.password),
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
