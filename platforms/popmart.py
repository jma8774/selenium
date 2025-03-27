import asyncio
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
from discordbot.main import sendBotChannel
from helper import try_get_json_value
from logger import log
from poller import Poller


class PopMart:
    def __init__(self):
        pass

    def check_for_have_a_seat(self):
        """Continuously check PopMart page for stock status"""
        with SB(uc=True, headless=False) as sb:
            log.info("Starting PopMart stock check...")
            last_notification_time = 0
            notification_interval = 5 * 60  # 5 minutes between notifications
            sb.open("https://www.popmart.com/us/pop-now/set/50")

            while True:
                try:
                    # Get the minute in the hour
                    minute = datetime.now().minute
                    if minute > 2 and minute < 58:
                        log.info(f"Not checking stock, they usually restock at XX:00")
                        time.sleep(15)
                        continue

                    if not sb.assert_text(
                        "THE MONSTERS - Have a Seat Vinyl Plush Blind Box",
                        timeout=60,
                    ):
                        source = sb.get_page_source()
                        log.warning(f"It messed up, source={source}")
                        sendBotChannel(f"It messed up, source={source}", user="jeemong")
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
