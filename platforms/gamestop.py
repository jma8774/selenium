import random
import threading
import time
from fake_useragent import UserAgent
import requests
from logger import log
from discordbot.main import sendBotChannel
from args import args
from poller import Poller
from helper import try_get_json_value
from database.main import TargetDB
from urllib.parse import urlencode

class GameStop:
  def __init__(self, db: TargetDB):
    self.db = db
    self.poller_data = [
      {
        "product_name": "Pokemon Trading Card Game: Destined Rivals Elite Trainer Box",
        "product_url": "https://www.gamestop.com/on/demandware.store/Sites-gamestop-us-Site/default/Product-Variation?dwvar_C200309_condition=New&pid=20021586&quantity=1&rt=productDetailsRedesign",
        "poll_url": "https://www.gamestop.com/on/demandware.store/Sites-gamestop-us-Site/default/Product-Variation?dwvar_C200309_condition=New&pid=20021586&quantity=1&rt=productDetailsRedesign",
      },
    ]

  def start_poll_for_stock(self):
    for poller in self.poller_data:
      poller = Poller(
        product_name=poller["product_name"],
        product_url=poller["product_url"],
        poll_url=poller["poll_url"],
        check_fn=self.check_fn,
        on_in_stock=self.on_in_stock
      )
      poller.start_poll()

  def check_fn(self, response: requests.Response) -> bool:
    json = response.json()
    log.info(json)
    return False
    json = response.json()
    shipping_options = json.get("data", {}).get("product", {}).get("fulfillment", {}).get("shipping_options", {})
    return (
      not shipping_options.get("availability_status") == "PRE_ORDER_UNSELLABLE" and
      (shipping_options.get("availability_status") == "IN_STOCK" or shipping_options.get("available_to_promise_quantity", 0) > 0)
    )


  def on_in_stock(self, poller: Poller, response):
    interval = 5 * 60 # 5 minutes
    json = response.json()
    amt = json.get("data", {}).get("product", {}).get("fulfillment", {}).get("shipping_options", {}).get("available_to_promise_quantity", 0)
    log.info(f"\t{poller.product_url}\n")
    if not args.dev and (not poller.product_url in self.last_in_stock_time or time.time() - self.last_in_stock_time[poller.product_url] > interval):
      sendBotChannel(f"✅ Item is in stock ({amt}): {poller.product_url}", role="chodes")
      self.last_in_stock_time[poller.product_url] = time.time()
    # if not poller.is_done and poller.should_handle:
      # log.info(f"Handling {poller.product_url}")
      # handle_target(poller.product_url)

