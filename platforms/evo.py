import json
import random
import re
import threading
import time
import traceback
from datetime import datetime
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from seleniumbase import SB

from args import args
from database.main import EvoDB
from discordbot.main import sendBotChannel, sendEmbed
from helper import try_get_json_value
from logger import log
from poller import Poller


class Evo:
    def __init__(self, db: EvoDB):
        self.db = db

    def check_for_price_drop(self):
        def check_for_have_a_seat_fn():
            with SB(test=True, uc=True, headless=True) as sb:
                log.info("Starting Evo price check...")
                sb.open(
                    "https://www.evo.com/shop/snowboard/jackets/686/burton/mens/size_s/size_xs/rpp_200"
                )
                while True:
                    try:
                        if not sb.assert_text("Men's Snowboard Jackets", timeout=60):
                            source = sb.get_page_source()
                            log.warning(f"[Evo] It messed up, source={source}")
                            sendBotChannel(
                                f"[Evo] It messed up, source={source}", user="jeemong"
                            )
                            sb.refresh_page()
                            continue

                        # Get page source and check stock status
                        source = sb.get_page_source()

                        # Get all product (div with "product-thumb js-product-thumb" class)
                        soup = BeautifulSoup(source, "html.parser")
                        products = soup.find_all("div", class_="product-thumb")
                        for product in products:
                            product_id = product.get("data-productid")
                            product_name = product.find(
                                "span", class_="product-thumb-title"
                            ).text
                            product_url = product.find(
                                "a", class_="product-thumb-link"
                            )["href"]
                            product_img = product.find(
                                "span",
                                class_="product-thumb-image-wrapper js-product-thumb-link",
                            ).find("img")["src"]

                            # Find the prices
                            prices = {"min": None, "max": None}
                            product_price_span = product.find(
                                lambda x: x
                                and x.name == "span"
                                and len(x.get("class", [])) == 1
                                and x.get("class", [])[0] == "product-thumb-price"
                            )

                            for maybe_price_span in product_price_span.children:
                                if "$" in (maybe_price_span.text or ""):
                                    price = maybe_price_span.find(
                                        text=True, recursive=False
                                    ).strip()[1:]
                                    if prices["min"] is None:
                                        prices["min"] = float(price)
                                    else:
                                        prices["max"] = float(price)
                            prices["max"] = prices["max"] or prices["min"]
                            # log.info(f"product_id={product_id} product_name={product_name} product_url={product_url} prices={prices}")

                            old_product = self.db.get(product_id)
                            new_product = None
                            if old_product is None:
                                new_product = self.db.insert_or_update_product(
                                    product_id, product_name, product_url, prices
                                )
                            elif (
                                old_product["price_history"][-1]["min"] != prices["min"]
                                or old_product["price_history"][-1]["max"]
                                != prices["max"]
                            ):
                                new_product = self.db.insert_or_update_product(
                                    product_id, product_name, product_url, prices
                                )
                            if new_product is not None:
                                price_history_string = "\n".join(
                                    [
                                        f"**{price['date']}:** ${price['min']} - ${price['max']}"
                                        for price in new_product["price_history"]
                                    ]
                                )
                                log.info(
                                    f"✅ Updated product_id={product_id} prices={prices}"
                                )
                                # sendBotChannel(
                                #     f"✅ Updated: https://www.evo.com{product_url}\n\n**Price History**\n{price_history_string}"
                                # )
                                sendEmbed(
                                    "✅ Updated Price",
                                    product_name,
                                    price_history_string,
                                    f"https://www.evo.com{product_url}",
                                    product_img,
                                )

                        delay = 60 * 60
                        log.info(f"Waiting {delay:.2f} seconds before next check...")
                        time.sleep(delay)

                        # Refresh the page
                        sb.refresh_page()

                    except Exception as e:
                        log.error(
                            f"Error during Evo check: {str(e)}, stacktrace={traceback.format_exc()}"
                        )
                        # Wait a bit longer on error
                        time.sleep(10)
                        continue

        threading.Thread(target=check_for_have_a_seat_fn, daemon=True).start()
