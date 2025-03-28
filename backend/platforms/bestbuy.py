import re
from seleniumbase import SB
from database.main import CommonDB
from discordbot.main import sendEmbed
from logger import log


class BestBuy:
    def __init__(self, db: CommonDB):
        self.db = db

    def check_for_airpods(self):
        log.info("Checking for AirPods Pro 2 Sale")

        with SB(uc=True, headless=True) as sb:
            sb.open(
                "https://www.bestbuy.com/site/apple-airpods-pro-2-wireless-active-noise-cancelling-earbuds-with-hearing-aid-feature-white/6447382.p?skuId=6447382"
            )
            try:
                product_name = sb.get_text("h1.heading-4.leading-6.font-500").strip()
                product_url = sb.get_current_url()
                product_img = (
                    sb.get("img.primary-image").get_attribute("src")
                    if sb.get("img.primary-image")
                    else None
                )

                # Get current lowest prices from the database
                lowest_regular_price = self.db.get(
                    "airpods_pro_2_lowest_regular_price", None
                )
                lowest_discounted_price = self.db.get(
                    "airpods_pro_2_lowest_discounted_price", None
                )
                sale_active = self.db.get(
                    "airpods_pro_2_sale_active", False
                )  # Sale state

                # Check if the "savings" test-id exists (indicating a sale is active)
                try:
                    sb.wait_for_element_visible('[data-testid="savings"]', timeout=10)
                    is_sale_active = sb.is_element_visible('[data-testid="savings"]')
                except:
                    is_sale_active = False  # If not found, assume no sale is active

                # Try to get the regular price; if not found, use customer price
                regular_price = (
                    sb.get_text('[data-testid="regular-price"]', timeout=2).strip()
                    if sb.is_element_visible('[data-testid="regular-price"]')
                    else None
                )

                if not regular_price:
                    regular_price = (
                        sb.get_text('[data-testid="customer-price"]', timeout=2).strip()
                        if sb.is_element_visible('[data-testid="customer-price"]')
                        else None
                    )
                # Initialize discounted_price to None before trying to assign it
                discounted_price = None
                if is_sale_active:
                    # Get the discounted price only if a sale is active
                    discounted_price = (
                        sb.get_text('[data-testid="customer-price"]', timeout=2).strip()
                        if sb.is_element_visible('[data-testid="customer-price"]')
                        else None
                    )
                    self.db.set(
                        "airpods_pro_2_sale_active", True
                    )  # Mark sale as active

                else:
                    log.info("Discounted price is gone. Marking sale as inactive.")
                    self.db.set("airpods_pro_2_sale_active", False)

                # Extract only numerical price values
                cleaned_regular_price = (
                    re.search(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", regular_price)
                    if regular_price
                    else None
                )

                cleaned_discounted_price = (
                    re.search(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", discounted_price)
                    if discounted_price
                    else None
                )

                # Determine the current prices
                regular_price_value = (
                    float(cleaned_regular_price.group().replace(",", ""))
                    if cleaned_regular_price
                    else None
                )
                discounted_price_value = (
                    float(cleaned_discounted_price.group().replace(",", ""))
                    if cleaned_discounted_price
                    else None
                )

                # Check for lowest prices and update accordingly
                updated = False
                price_tag = "Regular Price"

                if discounted_price_value and (
                    lowest_discounted_price is None
                    or discounted_price_value <= lowest_discounted_price
                ):
                    self.db.set(
                        "airpods_pro_2_lowest_discounted_price",
                        discounted_price_value,
                    )
                    log.info(f"New lowest discounted price: {discounted_price_value}")
                    updated = True
                    price_tag = "Discounted Price"

                # Send an alert only if needed
                if updated and not sale_active:
                    sendEmbed(
                        f"✅ New Lowest {price_tag}",
                        product_name,
                        f"${discounted_price_value if discounted_price_value else regular_price_value}",
                        product_url,
                        product_img,
                    )

            except Exception as e:
                log.error("Error: Could not find the price elements.")
                log.error(str(e))
