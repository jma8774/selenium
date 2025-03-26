import random
import threading
import time
import traceback
from fake_useragent import UserAgent
import requests
from logger import log
import discordbot.main as discordbot
from discordbot.main import sendBotChannel
from args import args
from poller import Poller
from helper import try_get_json_value
from database.main import CommonDB
from urllib.parse import urlencode
import json
from seleniumbase import SB
import re
from datetime import datetime
from bs4 import BeautifulSoup

class BrainyQuote:
  def __init__(self, db: CommonDB):
    self.db = db

  def check_for_daily_quote(self):
    def check_for_daily_quote_fn():
      with SB(test=True, uc=True, headless=True) as sb:
        last_quote = self.db.get("quote_of_the_day")
        sb.open("https://www.brainyquote.com/quote_of_the_day")

        if not sb.assert_text("Quote of the Day", timeout=60):
          log.error("Failed to open Quote of the Day page")
          # sendBotChannel("Failed to open Quote of the Day page", user="jeemong")
          return

        source = sb.get_page_source()
        soup = BeautifulSoup(source, "html.parser")
        quote_container = soup.find("div", class_="qotd-wrapper-cntr")
        quote_author = quote_container.find("a", title="view author").text
        quote_text = quote_container.find("a").find("div").find(text=True, recursive=False).strip()

        if last_quote and last_quote["quote"] == quote_text and last_quote["author"] == quote_author:
          log.info("Quote of the Day already checked today")
          return

        log.info(f"Quote of the Day: {quote_text} - {quote_author}")
        discordbot.send("lounge", f"**Quote of the Day**\n> “{quote_text}”\n> — {quote_author}")
        self.db.set("quote_of_the_day", {
          "quote": quote_text,
          "author": quote_author,
        })

    while True:
      threading.Thread(target=check_for_daily_quote_fn, daemon=True).start()
      time.sleep(60 * 60)
