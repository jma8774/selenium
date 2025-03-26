import random
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from logger import log


class ProxyManager:
    def __init__(self):
        load_dotenv()
        self.proxies = []

        # Get proxies from environment variable
        proxies_str = os.getenv("PROXIES")
        if not proxies_str:
            log.info("No PROXIES found in environment variables")
            return

        try:
            # Remove newlines and extra whitespace
            proxies_str = proxies_str.strip()
            # Parse the JSON array
            self.proxies = json.loads(proxies_str)
            if not self.proxies:
                log.info("Empty proxy list in environment variable")
                return
            log.info(f"Loaded {len(self.proxies)} proxies from environment")
        except Exception as e:
            log.error(f"Error loading proxies from environment: {str(e)}")
            log.info("No valid proxies found")

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy in requests format, or None if no proxies available"""
        if not self.proxies:
            return None

        proxy = random.choice(self.proxies)
        ip, port, username, password = proxy.split(":")
        return {
            "http": f"http://{username}:{password}@{ip}:{port}",
            "https": f"http://{username}:{password}@{ip}:{port}",
        }

    def get_random_selenium_proxy(self) -> Optional[str]:
        """Get a random proxy in selenium format, or None if no proxies available"""
        if not self.proxies:
            return None

        proxy = random.choice(self.proxies)
        ip, port, username, password = proxy.split(":")
        return f"{username}:{password}@{ip}:{port}"
