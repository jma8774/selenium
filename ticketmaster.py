import os
import random
import sys
import threading
import time

import pygame
import requests
from dotenv import load_dotenv
from seleniumbase import SB

from args import args
from logger import log
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

wait = None
driver = None


def click_join_queue_button(sb, time_to_wait=60 * 60):
    log.info("Starting to look for Join Queue button...")
    start_time = time.time()

    while True:
        try:
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.info(
                f"Attempting to find button... (Elapsed time: {elapsed_time:.1f}s)"
            )

            # Check if button exists and is clickable
            try:
                join_button = sb.find_element("//span[text()='Join the Queue']")
            except:
                log.warning("Button not found, waiting 15s before retrying...")
                sb.sleep(15)
                sb.refresh()
                continue

            if not join_button.is_enabled():
                log.warning("Button is not enabled, waiting 0.5s before retrying...")
                sb.sleep(0.5)
                continue

            log.info("Found Join Queue button, preparing to click...")

            # Hover and click with human-like behavior
            sb.hover_and_click(
                "//span[text()='Join the Queue']",
                "//span[text()='Join the Queue']",
            )

            log.info("Successfully clicked Join Queue button!")
            return True

        except Exception as e:
            log.warning(f"Error while trying to click button: {str(e)}")

            # Check for timeout
            if time.time() - start_time > time_to_wait:
                log.error(f"Timeout reached after {time_to_wait} seconds")
                raise TimeoutError("Timeout waiting for Join Queue button")

            sb.sleep(0.1)


def handle_ticketmaster(url):
    with SB(uc=True, headless=False, user_data_dir=os.getenv("USER_DATA_DIR")) as sb:
        try:
            log.info(f"Navigating to URL: {url}")
            sb.get(url)

            log.info("Starting automation steps...")
            sb.sleep(1)  # Wait for page to be ready

            # Try to click the Join Queue button
            click_join_queue_button(sb)

            # Play sound notification
            pygame.mixer.music.play(-1)
            sb.sleep(60 * 60)

        except Exception as e:
            log.error(f"An error occurred: {str(e)}")


def main():
    pygame.mixer.init()
    pygame.mixer.music.load("assets/ping.mp3")

    # Get the URL from arguments
    url = args.url
    log.info(f"Processing URL: {url}")

    # Handle the target URL
    handle_ticketmaster(url)


if __name__ == "__main__":
    load_dotenv()
    main()
