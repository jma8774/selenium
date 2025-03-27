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

import discordbot.main as discordbot
from args import args
from database.main import CommonDB
from discordbot.main import sendBotChannel
from helper import try_get_json_value
from logger import log
from poller import Poller


class AMD:
    def __init__(self, db: CommonDB):
        self.db = db

    def check_for_7600x3d(self):
        log.info("Checking for 7600x3D combo")

        last_checked = self.db.get("amd_7600x3d_last_checked")
        if False and last_checked and time.time() - last_checked < 60 * 60 * 24:
            log.info("7600x3d last checked less than 1 day ago, skipping...")
            return

        with SB(uc=True, headless=True) as sb:
            sb.open("https://www.microcenter.com/site/content/bundle-and-save.aspx")
            source = sb.get_page_source().lower()
            if "7600x3d" in source:
                log.info("✅ 7600x3D combo found at microcenter")
                sendBotChannel(
                    "✅ 7600x3D combo found at microcenter: https://www.microcenter.com/site/content/bundle-and-save.aspx",
                    user="jeemong",
                )
            else:
                log.info("❌ 7600x3D combo not found at microcenter")

            self.db.set("amd_7600x3d_last_checked", time.time())
