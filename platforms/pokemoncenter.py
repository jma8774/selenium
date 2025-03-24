import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    self.driver = webdriver.Chrome(options=options)
    log.info("Connected to existing Chrome instance")

  def start_poll_for_queue(self):
    def poll():
      while True:
        last_queue_time = self.db.get("last_queue_time")
        if last_queue_time and time.time() - last_queue_time < 60 * 60:
          log.info("Last queue time was less than 1 hour ago. Skipping...")
          time.sleep(60)
          continue

        try:
          log.info("Navigating to Pokemon Center...")
          self.driver.get("https://www.pokemoncenter.com")

          # Wait for page to load
          WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
          )

          try:
            # Check for queue message using multiple selectors
            queue_selectors = [
              "//h1[contains(@class, 'waiting-text')]",
              "//*[contains(text(), 'You are currently in line')]",
              "//*[contains(text(), 'queue-it')]"
            ]

            # First check main document
            for selector in queue_selectors:
              try:
                queue_element = WebDriverWait(self.driver, 2).until(
                  EC.presence_of_element_located((By.XPATH, selector))
                )
                if queue_element and queue_element.is_displayed():
                  log.info("[🔔] Queue detected! Drop likely happening.")
                  log.info(f"Found queue element with selector: {selector}")
                  sendBotChannel(f"🔔 Queue detected! Drop likely happening at https://www.pokemoncenter.com", role="king")
                  self.db.set("last_queue_time", time.time())
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
                    queue_element = WebDriverWait(self.driver, 2).until(
                      EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if queue_element and queue_element.is_displayed():
                      log.info("[🔔] Queue detected! Drop likely happening.")
                      log.info(f"Found queue element with selector: {selector} in iframe")
                      sendBotChannel(f"🔔 Queue detected! Drop likely happening at https://www.pokemoncenter.com", role="king")
                      self.db.set("last_queue_time", time.time())
                      self.driver.switch_to.default_content()
                      continue
                  except:
                    continue
              except:
                continue
              finally:
                self.driver.switch_to.default_content()

            log.info("[✅] Site is normal. No queue.")
            self.driver.get(random.choice(random_visits))
          except Exception as e:
            log.info(f"[⚠️] Page state unclear: {str(e)}")

        except Exception as e:
          log.error(f"Error checking Pokemon Center: {str(e)}")
          self.driver.get(random.choice(random_visits) )
        finally:
          time.sleep(60)  # Wait before next check

    thread = threading.Thread(target=poll)
    thread.daemon = True
    thread.start()
    return thread