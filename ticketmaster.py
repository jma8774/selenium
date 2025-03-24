import requests
import threading
import sys
import time
from logger import log
from discord.main import run_discord_bot, sendBotChannel
import random
from args import args
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import time
from dotenv import load_dotenv
import os
import pygame
wait = None
driver = None

def click_join_queue_button(time_to_wait=60 * 60):
    global driver, wait
    done = False
    start_time = time.time()

    log.info("Starting to look for Join Queue button...")
    while not done:
        try:
            current_time = time.time()
            elapsed_time = current_time - start_time
            log.info(f"Attempting to find button... (Elapsed time: {elapsed_time:.1f}s)")

            # Wait for the span with text "Join the Queue" to be present and clickable
            join_button = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//span[text()='Join the Queue']"
                ))
            )

            if not join_button.is_enabled():
                log.warning("Button is not enabled, waiting 0.05s before retrying...")
                time.sleep(0.05)
                continue
            else:
                log.debug("Found Join Queue button, preparing to click...")

            log.info("Found Join Queue button, preparing to click...")

            # Move to the button and click it with human-like movement
            actions = ActionChains(driver)
            actions.move_to_element(join_button)
            actions.pause(random.uniform(0.1, 0.3))  # Small pause before clicking
            actions.click()
            actions.perform()

            log.info("Successfully clicked Join Queue button!")
            done = True

        except Exception as e:
            log.warning(f"Error while trying to click button: {str(e)}")
            # Check if we've been waiting too long
            if time.time() - start_time > time_to_wait:
                log.error(f"Timeout reached after {time_to_wait} seconds")
                raise TimeoutError("Timeout waiting for Join Queue button")

        time.sleep(0.1)

def handle_ticketmaster(url):
    global wait, driver
    user_data_dir = os.getenv("USER_DATA_DIR")
    try:
        log.info("Connecting to existing Chrome instance...")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        log.info("Creating Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        log.info("Chrome driver created successfully")

        log.info(f"Navigating to URL: {url}")
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        log.info("Starting automation steps...")

        # Try to click the Join Queue button until it fails
        click_join_queue_button()

        pygame.mixer.music.play(-1)
        time.sleep(60)
    except Exception as e:
        log.info(f"An error occurred: {str(e)}")

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
