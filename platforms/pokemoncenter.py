import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from logger import log
from discord.main import sendBotChannel


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

    def simulate_human_interaction(self):
        viewport_width = self.driver.execute_script("return window.innerWidth;")
        viewport_height = self.driver.execute_script("return window.innerHeight;")

        def scroll_randomly():
            # Random scroll using ActionChains
            actions = ActionChains(self.driver)
            for _ in range(random.randint(1, 3)):
                scroll_amount = random.randint(50, 200)
                actions.scroll_by_amount(0, scroll_amount)
                actions.pause(random.uniform(0.5, 2))
            actions.perform()

        def move_mouse_randomly():
            # Random mouse movements using ActionChains
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 5)):
                x = random.randint(0, viewport_width)
                y = random.randint(0, viewport_height)
                actions.move_by_offset(x, y)
                actions.pause(random.uniform(0.2, 1))
            actions.perform()

        # Perform all actions in random order
        actions = [scroll_randomly, move_mouse_randomly]
        random.shuffle(actions)
        for action in actions:
            if random.random() < 0.5:
                action()
                time.sleep(random.uniform(0.5, 2))

    def start_poll_for_queue(self):
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        try:
            self.driver = webdriver.Chrome(options=options)

            # # Patch common WebDriver detection variables
            # self.driver.execute_cdp_cmd(
            #   'Page.addScriptToEvaluateOnNewDocument',
            #   {
            #     'source': '''
            #       Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            #       window.chrome = { runtime: {} };
            #       Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            #       Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            #     '''
            #   }
            # )

            log.info("Successfully connected to existing Chrome instance")
        except Exception as e:
            log.error(f"Failed to connect to Chrome: {str(e)}")
            log.info(
                "Make sure Chrome is running with: chrome.exe --remote-debugging-port=9222"
            )

        def poll():
            while True:
                seconds = 5 * 60
                last_detected_queue_time = self.db.get("last_detected_queue_time")
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
                    log.info("Navigating to Pokemon Center...")
                    self.driver.get("https://www.pokemoncenter.com")

                    # Wait for page to load
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.execute_script(
                            "return document.readyState"
                        )
                        == "complete"
                    )

                    # Delay DOM access and simulate human behavior
                    time.sleep(random.uniform(3, 10))
                    self.simulate_human_interaction()

                    try:
                        # Check for queue message using multiple selectors
                        queue_selectors = [
                            "//h1[contains(@class, 'waiting-text')]",
                            "//*[contains(text(), 'You are currently in line')]",
                            "//*[contains(text(), 'queue-it')]",
                        ]

                        # First check main document
                        for selector in queue_selectors:
                            try:
                                queue_element = WebDriverWait(
                                    self.driver, random.randint(1, 3)
                                ).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                if queue_element and queue_element.is_displayed():
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
                                    self.db.set("last_detected_queue_time", time.time())
                                    found_queue = True
                                    continue
                            except:
                                continue

                        # Then check all iframes
                        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                        for iframe in iframes:
                            try:
                                self.driver.switch_to.frame(iframe)
                                for selector in queue_selectors:
                                    try:
                                        queue_element = WebDriverWait(
                                            self.driver, random.randint(1, 3)
                                        ).until(
                                            EC.presence_of_element_located(
                                                (By.XPATH, selector)
                                            )
                                        )
                                        if (
                                            queue_element
                                            and queue_element.is_displayed()
                                        ):
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
                                                "last_detected_queue_time", time.time()
                                            )
                                            found_queue = True
                                            self.driver.switch_to.default_content()
                                            continue
                                    except:
                                        continue
                            except:
                                continue
                            finally:
                                self.driver.switch_to.default_content()

                        if not found_queue:
                            log.info("[✅] Site is normal. No queue.")
                            sendBotChannel(f"🔔 It fucked up", user="jeemong")
                            time.sleep(random.uniform(3, 10))
                            self.simulate_human_interaction()
                            self.driver.get(random.choice(random_visits))
                    except Exception as e:
                        log.info(f"[⚠️] Page state unclear: {str(e)}")

                except Exception as e:
                    log.error(f"Error checking Pokemon Center: {str(e)}")
                    try:
                        self.driver.get(random.choice(random_visits))
                    except:
                        log.error("Failed to navigate to random site after error")
                finally:
                    time.sleep(
                        random.randint(60, 90)
                    )  # Wait random amount of time before next check

        thread = threading.Thread(target=poll)
        thread.daemon = True
        thread.start()
        return thread
