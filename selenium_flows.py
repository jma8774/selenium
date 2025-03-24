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
from logger import log

in_progress = False
wait = None
driver = None

def click_element(locator, delay=True):
    global wait, driver
    while True:
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            if not element.is_enabled():
                time.sleep(0.1)
                continue
            actions = ActionChains(driver)
            actions.move_to_element(element)
            if delay:
                actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            return element
        except:
            time.sleep(0.1)
            continue

def write_input(locator, text, delay=True):
    global wait, driver
    while True:
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            if not element.is_enabled():
                time.sleep(0.1)
                continue
            actions = ActionChains(driver)
            actions.move_to_element(element)
            if delay:
                actions.pause(random.uniform(0.1, 0.3))
            actions.send_keys(text)
            actions.perform()
            return element
        except:
            time.sleep(0.1)
            continue

def handle_target(url):
    global wait, driver, in_progress
    if in_progress:
        log.info("Already in progress, skipping...")
        return
    in_progress = True
    cc_number = os.getenv("CC_NUMBER")
    expiration_date = os.getenv("EXPIRATION_DATE") 
    cvv = os.getenv("CVV")
    user_data_dir = os.getenv("USER_DATA_DIR")

    try:
        log.info("Initializing Chrome driver...")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        log.info("Creating Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        log.info("Chrome driver created successfully")
        
        log.info(f"Navigating to URL: {url}")
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        log.info("Starting automation steps...")
        # Click shipping option
        click_element((By.XPATH, "//span[text()='Shipping']"))

        # Add to cart
        click_element((By.XPATH, "//button[text()='Add to cart']"))

        # View cart
        click_element((By.XPATH, "//a[text()='View cart & check out']"))

        # Checkout
        click_element((By.XPATH, "//button[text()='Check out']"))

        # Place order
        click_element((By.XPATH, "//button[text()='Place your order']"))

        # Enter CVV
        write_input((By.ID, "enter-cvv"), cvv)

        # Confirm
        click_element((By.XPATH, "//button[text()='Confirm']"))
        
    except Exception as e:
        log.info(f"An error occurred: {str(e)}")
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass
        in_progress = False
