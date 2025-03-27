import random
import threading
import time

from seleniumbase import SB

from discordbot.main import sendBotChannel
from logger import log

random_visits = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://www.twitter.com",
    "https://www.linkedin.com",
    "https://www.github.com",
]


class PokemonCenter:
    def __init__(self, db):
        self.db = db

    def start_poll_for_queue(self):
        def poll():
            with SB(uc=True, headless=False) as sb:
                try:
                    log.info("Successfully connected to Chrome instance")
                    log.info("Navigating to Pokemon Center...")
                    sb.get("https://www.pokemoncenter.com")

                    while True:
                        seconds = 5 * 60
                        last_detected_queue_time = self.db.get(
                            "last_detected_queue_time"
                        )
                        if (
                            last_detected_queue_time
                            and time.time() - last_detected_queue_time < seconds
                        ):
                            log.info(
                                f"Last queue time was less than {seconds} seconds ago. Skipping..."
                            )
                            time.sleep(60)
                            continue

                        try:
                            found_queue = False

                            # Ensure page is fully loaded before checking for queue
                            sb.sleep(10)

                            # Define selectors that indicate presence of a queue
                            queue_selectors = [
                                "h1.waiting-text",
                                "//*[contains(text(), 'You are currently in line')]",
                                "//*[contains(text(), 'queue-it')]",
                            ]

                            # First check the main page for queue indicators
                            for selector in queue_selectors:
                                try:
                                    # Handle both CSS and XPath selectors
                                    if selector.startswith("//"):
                                        exists = sb.is_element_visible(
                                            selector, by="xpath"
                                        )
                                    else:
                                        exists = sb.is_element_visible(selector)

                                    if exists:
                                        log.info(
                                            "[🔔] Queue detected! Drop likely happening."
                                        )
                                        log.info(
                                            f"Found queue element with selector: {selector}"
                                        )
                                        sendBotChannel(
                                            f"🔔 Queue detected! Drop likely happening at https://www.pokemoncenter.com",
                                            user="jeemong",
                                        )
                                        self.db.set(
                                            "last_detected_queue_time", time.time()
                                        )
                                        found_queue = True
                                        break
                                except:
                                    continue

                            # Check iframes for queue
                            if not found_queue:
                                iframes = sb.find_elements("iframe")
                                for iframe in iframes:
                                    try:
                                        sb.switch_to_frame(iframe)
                                        for selector in queue_selectors:
                                            try:
                                                if selector.startswith("//"):
                                                    exists = sb.is_element_visible(
                                                        selector, by="xpath"
                                                    )
                                                else:
                                                    exists = sb.is_element_visible(
                                                        selector
                                                    )

                                                if exists:
                                                    log.info(
                                                        "[🔔] Queue detected! Drop likely happening."
                                                    )
                                                    log.info(
                                                        f"Found queue element with selector: {selector} in iframe"
                                                    )
                                                    sendBotChannel(
                                                        f"🔔 Queue detected! Drop likely happening at https://www.pokemoncenter.com",
                                                        user="jeemong",
                                                    )
                                                    self.db.set(
                                                        "last_detected_queue_time",
                                                        time.time(),
                                                    )
                                                    found_queue = True
                                                    break
                                            except:
                                                continue
                                        sb.switch_to_default_content()
                                        if found_queue:
                                            break
                                    except:
                                        sb.switch_to_default_content()
                                        continue

                            if not found_queue:
                                log.info("[✅] Site is normal. No queue.")

                        except Exception as e:
                            log.error(f"Error checking Pokemon Center: {str(e)}")
                        finally:
                            time.sleep(random.randint(10, 15))
                            sb.refresh()

                except Exception as e:
                    log.error(f"Failed to connect to Chrome: {str(e)}")
                    log.info("Make sure Chrome is installed and available in PATH")

        thread = threading.Thread(target=poll)
        thread.daemon = True
        thread.start()
        return thread
