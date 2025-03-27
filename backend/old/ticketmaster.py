import os
import random

import pygame
from dotenv import load_dotenv
from seleniumbase import SB

from args import args
from discordbot.main import sendBotChannel
from logger import log


class TicketmasterBot(SB):
    def click_join_queue_button(self, time_to_wait=60 * 60):
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
                join_button_xpath = "//span[text()='Join the Queue']"
                if self.is_element_present(join_button_xpath, by="xpath", timeout=1):
                    if not self.is_element_clickable(
                        join_button_xpath, by="xpath", timeout=1
                    ):
                        log.warning(
                            "Button is not enabled, waiting 0.05s before retrying..."
                        )
                        self.sleep(0.05)
                        continue

                    log.info("Found Join Queue button, preparing to click...")

                    # Hover and click with human-like behavior
                    self.hover_and_click(join_button_xpath, by="xpath", timeout=10)
                    log.info("Successfully clicked Join Queue button!")
                    return True

            except Exception as e:
                log.warning(f"Error while trying to click button: {str(e)}")

                # Check for timeout
                if time.time() - start_time > time_to_wait:
                    log.error(f"Timeout reached after {time_to_wait} seconds")
                    raise TimeoutError("Timeout waiting for Join Queue button")

                self.sleep(0.1)

    def run_bot(self, url):
        try:
            log.info(f"Navigating to URL: {url}")
            self.get(url)

            log.info("Starting automation steps...")
            self.wait_for_ready_state_complete()

            # Try to click the Join Queue button
            self.click_join_queue_button()

            # Play sound notification
            pygame.mixer.music.play(-1)
            self.sleep(60)

        except Exception as e:
            log.error(f"An error occurred: {str(e)}")
            raise e


def main():
    # Initialize sound
    pygame.mixer.init()
    pygame.mixer.music.load("assets/ping.mp3")

    # Get URL from arguments
    url = args.url
    log.info(f"Processing URL: {url}")

    # Run the bot
    with SB(uc=True, headless=False) as sb:
        bot = TicketmasterBot(sb)
        bot.run_bot(url)


if __name__ == "__main__":
    load_dotenv()
    main()
