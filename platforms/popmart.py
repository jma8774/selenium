import json
import random
import re
import threading
import time
from datetime import datetime
from urllib.parse import urlencode

import requests
from fake_useragent import UserAgent
from seleniumbase import SB

from args import args
from database.main import TargetDB
from discord.main import sendBotChannel
from helper import try_get_json_value
from logger import log
from poller import Poller


class PopMart:
    def __init__(self):
        self.session = requests.Session()
        self.poller_data = [
            {
                "product_name": "Pokemon Trading Card Game: Destined Rivals Elite Trainer Box",
                "product_url": "https://www.gamestop.com/on/demandware.store/Sites-gamestop-us-Site/default/Product-Variation?dwvar_C200309_condition=New&pid=20021586&quantity=1&rt=productDetailsRedesign",
                "poll_url": "https://www.gamestop.com/on/demandware.store/Sites-gamestop-us-Site/default/Product-Variation?dwvar_C200309_condition=New&pid=20021586&quantity=1&rt=productDetailsRedesign",
            },
        ]
        self.last_in_stock_time = {}

    def check_for_have_a_seat(self):
        def check_for_have_a_seat_fn():
            """Continuously check PopMart page for stock status"""
            with SB(test=True, uc=True, headless=False) as sb:
                log.info("Starting PopMart stock check...")
                last_notification_time = 0
                notification_interval = 5 * 60  # 5 minutes between notifications
                sb.open("https://www.popmart.com/us/pop-now/set/50")

                while True:
                    try:
                        # Get the minute in the hour
                        minute = datetime.now().minute
                        log.info(f"Minute: {minute}")
                        if minute > 2 and minute < 58:
                            log.info(
                                f"Not checking stock, they usually restock at XX:00"
                            )
                            time.sleep(15)
                            continue

                        if not sb.assert_text(
                            "THE MONSTERS - Have a Seat Vinyl Plush Blind Box",
                            timeout=60,
                        ):
                            source = sb.get_page_source()
                            log.warning(f"It messed up, source={source}")
                            sendBotChannel(
                                f"It messed up, source={source}", user="jeemong"
                            )
                            sb.refresh_page()
                            continue

                        # Get page source and check stock status
                        source = sb.get_page_source()
                        current_time = time.time()

                        # Find all string in source that match "https://cdn-global.popmart.com/images/boxPC/bigBox/smallBoxLockIcon.png"
                        # lock_icons = re.findall(r'https://cdn-global\.popmart\.com/images/boxPC/bigBox/smallBoxLockIcon\.png', source)
                        # log.info(f"Lock icons: {lock_icons}")

                        if "NOTIFY ME WHEN AVAILABLE" not in source:
                            log.info("✅ Item is in stock!")
                            if (
                                current_time - last_notification_time
                                > notification_interval
                            ):
                                sendBotChannel(
                                    "✅ Item is in stock: https://www.popmart.com/us/pop-now/set/50",
                                    user="jeemong",
                                )
                                last_notification_time = current_time
                        else:
                            log.info("❌ Item is not in stock")

                        # Random delay between checks (15 - 30 seconds)
                        minute = datetime.now().minute
                        seconds = datetime.now().second
                        if minute == 59 and seconds > 30:
                            delay = 60 - seconds + 2
                        elif minute == 0:
                            delay = random.uniform(5, 15)
                        else:
                            delay = random.uniform(15, 30)
                        log.info(f"Waiting {delay:.2f} seconds before next check...")
                        time.sleep(delay)

                        # Refresh the page
                        sb.refresh_page()

                    except Exception as e:
                        log.error(f"Error during PopMart check: {str(e)}")
                        # Wait a bit longer on error
                        time.sleep(10)
                        continue

        threading.Thread(target=check_for_have_a_seat_fn, daemon=True).start()

    def start_poll_for_stock(self):
        for poller_data in self.poller_data:
            poller = Poller(
                product_name=poller_data["product_name"],
                product_url=poller_data["product_url"],
                poll_url=poller_data["poll_url"],
                check_fn=self.check_fn,
                on_in_stock=self.on_in_stock,
            )
            poller.start_poll()

    def check_fn(self, response: requests.Response) -> bool:
        try:
            json = response.json()
            log.info(f"PopMart response: {json}")
            # TODO: Implement proper stock check logic based on PopMart's response format
            return False
        except Exception as e:
            log.error(f"Error parsing PopMart response: {str(e)}")
            return False

    def on_in_stock(self, poller: Poller, response):
        interval = 5 * 60  # 5 minutes
        try:
            json = response.json()
            # TODO: Implement proper stock amount check based on PopMart's response format
            amt = 1  # Placeholder
            log.info(f"\t{poller.product_url}\n")
            if not args.dev and (
                not poller.product_url in self.last_in_stock_time
                or time.time() - self.last_in_stock_time[poller.product_url] > interval
            ):
                sendBotChannel(
                    f"✅ Item is in stock ({amt}): {poller.product_url}", role="chodes"
                )
                self.last_in_stock_time[poller.product_url] = time.time()
        except Exception as e:
            log.error(f"Error in PopMart on_in_stock: {str(e)}")
