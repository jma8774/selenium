import re

from seleniumbase import SB

from database.main import CommonDB
from discordbot.main import sendEmbed
from logger import log


class BestBuy:
    def __init__(self, db: CommonDB):
        self.db = db

    def check_for_airpods(self):
        log.info("Checking for airpod pros 2 Sale")

        with SB(uc=True, headless=True) as sb:
            sb.open(
                "https://www.bestbuy.com/site/apple-airpods-pro-2-wireless-active-noise-cancelling-earbuds-with-hearing-aid-feature-white/6447382.p?skuId=6447382"
            )
            try:
                product_name = sb.get_text("h1.heading-4.leading-6.font-500").strip()
                product_url = sb.get_current_url()
                # Get the lowest price from the database
                lowest_price = self.db.get("airpods_pro_2_lowest_price", 9999)
                product_img = (
                    sb.get("img.primary-image").get_attribute("src")
                    if sb.get("img.primary-image")
                    else None
                )

                # Locate the regular price element
                regular_price = sb.get_text('[data-testid="regular-price"]').strip()
                discounted_price = sb.get_text('[data-testid="customer-price"]').strip()

                # Extract only the numerical price (no $ sign)
                cleaned_regular_price = re.search(
                    r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", regular_price
                )

                # If discounted price exists, use it, otherwise use the regular price
                price_to_compare = None

                if discounted_price:
                    cleaned_discounted_price = re.search(
                        r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", discounted_price
                    )
                    if cleaned_discounted_price:
                        price_to_compare = cleaned_discounted_price.group().replace(
                            ",", ""
                        )
                else:
                    if cleaned_regular_price:
                        regular_price = cleaned_regular_price.group().replace(",", "")
                        price_to_compare = regular_price

                if price_to_compare:
                    price_to_compare_float = float(price_to_compare)

                    # Compare the selected price (discounted or regular) to the lowest price
                    if price_to_compare_float < lowest_price:
                        self.db.set("airpods_pro_2_lowest_price", price_to_compare)
                        log.info(f"Lowest price updated: {price_to_compare}")

                        sendEmbed(
                            "✅ Currently Discounted",
                            product_name,
                            f"${price_to_compare}",
                            product_url,
                            product_img,
                        )

                else:
                    log.info("Price not found")

            except Exception as e:
                log.info("Error: Could not find the regular price element.")
                log.info(e)
