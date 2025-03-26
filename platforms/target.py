import random
import threading
import time
from urllib.parse import urlencode

import requests
from fake_useragent import UserAgent

from args import args
from database.main import TargetDB
from discord.main import sendBotChannel
from helper import try_get_json_value
from logger import log
from poller import Poller


class Target:
    def __init__(self, target_db: TargetDB):
        self.target_db = target_db
        self.poller_data = [
            {
                "product_name": "Pokémon Trading Card Game: Scarlet & Violet—Prismatic Evolutions Elite Trainer Box",
                "product_url": "https://www.target.com/p/2024-pok-scarlet-violet-s8-5-elite-trainer-box/-/A-93954435",
                "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=93954435&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3356&paid_membership=false&base_membership=true&card_membership=false&required_store_id=3356&visitor_id=01954AAD38E1020192C9505DA3D40B51&channel=WEB&page=%2Fp%2FA-93954435",
            },
            {
                "product_name": "Pokémon Trading Card Game: Scarlet & Violet 151 Ultra-Premium Collection",
                "product_url": "https://www.target.com/p/pokemon-trading-card-game-scarlet-38-violet-151-ultra-premium-collection/-/A-88897906#lnk=sametab",
                "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=88897906&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3356&paid_membership=false&base_membership=true&card_membership=false&required_store_id=3356&visitor_id=01954AAD38E1020192C9505DA3D40B51&channel=WEB&page=%2Fp%2FA-88897906",
            },
            {
                "product_name": "Pokémon Trading Card Game: Scarlet & Violet 151 Elite Trainer Box",
                "product_url": "https://www.target.com/p/pokemon-trading-card-game-scarlet-38-violet-151-elite-trainer-box/-/A-88897899#lnk=sametab",
                "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=88897899&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3356&paid_membership=false&base_membership=true&card_membership=false&required_store_id=3356&visitor_id=01954AAD38E1020192C9505DA3D40B51&channel=WEB&page=%2Fp%2FA-88897899",
            },
            {
                "product_name": "Pokémon Trading Card Game: Scarlet & Violet S3.5 Booster Bundle Box",
                "product_url": "https://www.target.com/p/tempo/-/A-88897904?nrtv_cid=wsavemyynqysm",
                "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=88897904&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3356&paid_membership=false&base_membership=true&card_membership=false&required_store_id=3356&visitor_id=01954AAD38E1020192C9505DA3D40B51&channel=WEB&page=%2Fp%2FA-88897904",
            },
            {
                "product_name": "Pokémon Trading Card Game: Scarlet & Violet— Journey Together Elite Trainer Box",
                "product_url": "https://www.target.com/p/2025-pok-233-mon-scarlet-violet-s9-elite-trainer-box/-/A-93803439#lnk=sametab",
                "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=93803439&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3243&paid_membership=false&base_membership=false&card_membership=false&required_store_id=3356&visitor_id=01954AAD38E1020192C9505DA3D40B51&channel=WEB&page=%2Fp%2FA-93803439",
            },
            {
                "product_name": "Pokémon Trading Card Game: Scarlet & Violet— Paldean Fates Elite Trainer Box",
                "product_url": "https://www.target.com/p/pok-233-mon-trading-card-game-scarlet-38-violet-8212-paldean-fates-elite-trainer-box/-/A-89432659",
                "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=89432659&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3356&paid_membership=false&base_membership=true&card_membership=false&required_store_id=3356&visitor_id=0195BA32AFD70201B5038D6F2E99042B&channel=WEB&page=%2Fp%2FA-89432",
            },
            # {
            #   "product_name": "Pokémon Trading Card Game: Scarlet & Violet—Prismatic Evolutions Super-Premium Collection",
            #   "product_url": "https://www.target.com/p/pok-233-mon-trading-card-game-scarlet-38-violet-8212-prismatic-evolutions-super-premium-collection/-/A-94300072",
            #   "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=94300072&store_id=3356&zip=11223&state=NY&latitude=40.590296&longitude=-73.981104&scheduled_delivery_store_id=3356&paid_membership=false&base_membership=true&card_membership=false&required_store_id=3356&visitor_id=0195BA32AFD70201B5038D6F2E99042B&channel=WEB&page=%2Fp%2FA-94300072",
            # }
        ]

        if args.dev:
            self.poller_data.append(
                {
                    "product_name": "Ultra-Pro Pokémon Trading Card Game Scarlet Violet Twilight Masquerade 9-Pocket Portfolio",
                    "product_url": "https://www.target.com/p/ultra-pro-pok-233-mon-trading-card-game-scarlet-violet-twilight-masquerade-9-pocket-portfolio/-/A-92436711#lnk=sametab",
                    "poll_url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&is_bot=false&tcin=92436711&store_id=322&zip=94043&state=CA&latitude=37.410&longitude=-122.080&scheduled_delivery_store_id=322&paid_membership=false&base_membership=false&card_membership=false&required_store_id=322&visitor_id=0195BA32AFD70201B5038D6F2E99042B&channel=WEB&page=%2Fp%2FA-92436711",
                }
            )
            self.last_in_stock_time = {}

    def start_poll_for_stock(self):
        for poller in self.poller_data:
            poller = Poller(
                product_name=poller["product_name"],
                product_url=poller["product_url"],
                poll_url=poller["poll_url"],
                check_fn=self.check_fn,
                on_in_stock=self.on_in_stock,
            )
            poller.start_poll()

    def start_poll_for_new_product(self, interval: int = 10 * 60):
        def compute_full_url(user_agent: str, offset: int):
            params = {
                "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
                "channel": "WEB",
                "count": "24",
                "default_purchasability_filter": "true",
                "include_dmc_dmr": "true",
                "include_sponsored": "true",
                "include_review_summarization": "false",
                "keyword": "pokemon cards",
                "new_search": "true",
                "offset": offset,
                "page": "/s/pokemon cards",
                "platform": "desktop",
                "pricing_store_id": "3243",
                "spellcheck": "true",
                "store_ids": "3243,3429,2212,3326,3276",
                "useragent": user_agent,
                "visitor_id": "0195C9520FF60201A3FB4D0742268149",
                "zip": "11223",
            }
            return f"https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?{urlencode(params)}"

        def poll():
            last_poll_time = self.target_db.get("last_poll_time")
            if last_poll_time and time.time() - last_poll_time < interval:
                log.info(f"Last poll was less than {interval} seconds ago. Skipping...")
                time.sleep(interval)
                return
            ua = UserAgent()
            while True:
                db_tcins = set(self.target_db.get("tcins") or [])
                offset = 0
                total = 9999999  # Initial value of infinite
                headers = {"User-Agent": ua.random, "Accept": "application/json"}
                url = (
                    "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
                )
                try:
                    while offset < total:
                        log.info(f"Polling Target for new products: {offset} / {total}")
                        full_url = compute_full_url(headers["User-Agent"], offset)
                        response = requests.get(
                            full_url,
                            headers=headers,
                            timeout=10,
                        )
                        response.raise_for_status()
                        if response.status_code != 200:
                            log.error(
                                f"❌ Target returned status code {response.status_code} for {full_url}"
                            )
                            log.error(response)
                            continue
                        json = response.json()
                        total = (
                            try_get_json_value(
                                json,
                                "data.search.search_response.metadata.total_results",
                            )
                            or 9999999
                        )
                        products = (
                            try_get_json_value(json, "data.search.products") or []
                        )
                        for product in products:
                            title = try_get_json_value(
                                product, "item.product_description.title"
                            )
                            buy_url = try_get_json_value(
                                product, "item.enrichment.buy_url"
                            )
                            tcin = try_get_json_value(product, "tcin")
                            if tcin not in db_tcins:
                                log.info(f"🆕 New product: {title} ({tcin}): {buy_url}")
                                sendBotChannel(
                                    f"🆕 New product: {title} ({tcin}): {buy_url}"
                                )
                                db_tcins.add(tcin)
                        offset += 24
                        time.sleep(0.25)
                except Exception as e:
                    log.error(f"Error polling Target: {str(e)}")
                self.target_db.set("tcins", db_tcins)
                self.target_db.set("last_poll_time", time.time())
                log.info(
                    f"🔄 Done polling Target for new products, sleeping for {interval} seconds"
                )
                time.sleep(interval)

        thread = threading.Thread(target=poll)
        thread.daemon = True
        thread.start()
        return thread

    def check_fn(self, response: requests.Response) -> bool:
        json = response.json()
        shipping_options = (
            json.get("data", {})
            .get("product", {})
            .get("fulfillment", {})
            .get("shipping_options", {})
        )
        return not shipping_options.get(
            "availability_status"
        ) == "PRE_ORDER_UNSELLABLE" and (
            shipping_options.get("availability_status") == "IN_STOCK"
            or shipping_options.get("available_to_promise_quantity", 0) > 0
        )

    def on_in_stock(self, poller: Poller, response):
        interval = 5 * 60  # 5 minutes
        json = response.json()
        amt = (
            json.get("data", {})
            .get("product", {})
            .get("fulfillment", {})
            .get("shipping_options", {})
            .get("available_to_promise_quantity", 0)
        )
        log.info(f"\t{poller.product_url}\n")
        if not args.dev and (
            not poller.product_url in self.last_in_stock_time
            or time.time() - self.last_in_stock_time[poller.product_url] > interval
        ):
            sendBotChannel(
                f"✅ Item is in stock ({amt}): {poller.product_url}", role="chodes"
            )
            self.last_in_stock_time[poller.product_url] = time.time()
        # if not poller.is_done and poller.should_handle:
        # log.info(f"Handling {poller.product_url}")
        # handle_target(poller.product_url)
