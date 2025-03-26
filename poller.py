import random
import threading
import time
from typing import Callable, Optional

import pygame
import requests
from fake_useragent import UserAgent

from args import args
from discord.main import sendBotChannel
from logger import log


class Poller:
    def __init__(
        self,
        product_name: str,
        product_url: str,
        poll_url: str,
        check_fn: Callable[[requests.Response], bool],
        interval_range: tuple = (3, 6),
        headers: Optional[dict] = None,
        proxies: Optional[dict] = None,
        on_in_stock: Optional[Callable[["Poller", requests.Response], None]] = None,
        handle: Optional[Callable[[], bool]] = True,
    ):
        """
        :param url: URL to poll
        :param check_fn: Function that checks if item is in stock, takes requests.Response -> bool
        :param interval_range: Tuple of (min_seconds, max_seconds) between polls
        :param headers: Optional headers to send
        :param proxies: Optional proxy dict for requests
        :param on_in_stock: Optional function to call when item is in stock
        """
        self.done = False
        self.handle = handle
        self.ua = UserAgent()
        self.product_name = product_name
        self.product_url = product_url
        self.poll_url = poll_url
        self.check_fn = check_fn
        self.interval_range = interval_range
        self.headers = headers or {
            "User-Agent": self.ua.random,
            "Accept": "application/json",
            # "Referer": "https://example.com"
        }
        self.proxies = proxies
        self.on_in_stock = on_in_stock

        self.pygame = pygame
        self.pygame.mixer.init()
        self.pygame.mixer.music.load("assets/ping.mp3")

    def poll(self):
        log.info(f"🔍 Started polling for {self.product_name}")
        if not args.dev:
            sendBotChannel(
                f"🔍 Started polling for {self.product_name}: {self.product_url}"
            )
            pass
        while True:
            try:
                response = requests.get(
                    self.poll_url,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=10,
                )
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 60))
                    log.info(f"⏳ Rate limited. Sleeping for {wait_time} seconds.")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                if self.check_fn(response):
                    log.info(f"✅ Item is in stock: {self.product_name}")
                    if self.on_in_stock:
                        self.pygame.mixer.music.play()
                        self.on_in_stock(self, response)
                        self.done = True
                    # break
                else:
                    log.info(f"❌ Still out of stock: {self.product_name}\n")
            except requests.RequestException as e:
                log.info(f"⚠️ Request failed: {e}")
                log.info(f"Response: {response.text}")

            delay = random.uniform(*self.interval_range)
            time.sleep(delay)
        time.sleep(1)

    @property
    def is_done(self):
        return self.done

    @property
    # This property determines whether selenium should handle the item
    def should_handle(self):
        return self.handle

    def start_poll(self):
        thread = threading.Thread(target=self.poll)
        thread.daemon = True
        thread.start()
        return thread
