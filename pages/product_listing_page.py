"""
Product Listing Page — Page Object Model
=========================================
Covers any product listing page on the platform:
    - Seller pages     (/seller/...)
    - Brand pages      (/brand/...)
    - Category pages   (/category/...)
    - Subcategory pages

All these page types share the same structure and CSS selectors
on this platform, making this class reusable across all of them.

Author: Abhiram Anish
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# ── CSS Selectors ──────────────────────────────────────────────────────────────

# Filter button selectors — use whichever matches the page type
CATEGORY_FILTER   = ".subcatsort"      # Category/Seller pages
SUB_CATEGORY      = ".thirdlcatsort"   # Sub-subcategory pages
BRAND_FILTER         = ".brandsort"       # Brand pages

# Product selectors
PRODUCT_CARD         = ".inner-pro-col"       # Product card on listing page
PRODUCT_LINK         = ".inner-pro-col > a"   # Clickable link on product card

# Product detail page selectors
SELLER_NAME          = "p.head.redclr"    # Seller name on product detail page
BRAND_NAME           = ".name a"          # Brand name on product detail page


# ── Page Object ────────────────────────────────────────────────────────────────

class ProductListingPage:
    """
    Page Object for any product listing page.
    Encapsulates all interactions so test files stay clean
    and only contain test logic.
    """

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def open(self, url):
        """Navigate to the given URL."""
        self.driver.get(url)

    def get_filters(self, filter_selector):
        """
        Wait for and return all filter button elements.
        Re-fetches every time to avoid stale element references
        after page navigation.

        Args:
            filter_selector: CSS selector for the filter type
                             e.g. CATEGORY_FILTER, BRAND_FILTER

        Returns:
            List of filter WebElements
        """
        return self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, filter_selector)
            )
        )

    def get_filter_name(self, filter_element, filter_type):
        """
        Extract the display name from a filter element.

        Args:
            filter_element: The filter WebElement
            attribute:      Data attribute holding the name
                            e.g. "data-subcat_name" or "data-bname"
        Returns:
            Name string or None
        """
        attribute=""
        if filter_type == ".brandsort" :
            attribute = "data-bname"
        else :
            attribute = "data-subcat_name" 
        return filter_element.get_attribute(attribute)

    def click_filter(self, filter_element):
        """
        Scroll filter into view and click it using JavaScript.
        JS click used because filter buttons can be partially hidden.
        Waits for URL to change confirming navigation happened.

        Args:
            filter_element: The filter WebElement to click
        """
        old_url = self.driver.current_url

        self.driver.execute_script(
            "arguments[0].scrollIntoView();", filter_element
        )
        self.driver.execute_script(
            "arguments[0].click();", filter_element
        )

        # Confirm navigation happened
        self.wait.until(lambda d: d.current_url != old_url)

    def scroll_to_load_all_products(self):
        """
        Handles infinite scroll — keeps scrolling until no new products load.
        Compares product count before and after each scroll to detect end of list.

        Returns:
            Final total product count
        """
        previous_count = 0

        while True:
            products = self.driver.find_elements(
                By.CSS_SELECTOR, PRODUCT_CARD
            )
            current_count = len(products)

            # No new products loaded — reached end of list
            if current_count == previous_count:
                break

            previous_count = current_count

            # Scroll to bottom to trigger lazy load
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            try:
                # Wait until new products appear
                self.wait.until(
                    lambda d: len(
                        d.find_elements(By.CSS_SELECTOR, PRODUCT_CARD)
                    ) > previous_count
                )
            except Exception:
                # Timeout — no more products loading
                break

        return previous_count

    def get_product_links(self):
        """
        Collect all product URLs from the current listing page.

        Returns:
            List of product URLs (strings)
        """
        elements = self.driver.find_elements(By.CSS_SELECTOR, PRODUCT_LINK)
        return [el.get_attribute("href") for el in elements]

    def get_seller_name(self, product_url):
        """
        Navigate to a product page and return the seller name.

        Args:
            product_url: URL of the product detail page

        Returns:
            Seller name in lowercase, or None if not found
        """
        self.driver.get(product_url)
        try:
            element = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, SELLER_NAME)
                )
            )
            return " ".join(element.text.lower().split())
        except Exception:
            return None

    def get_brand_name(self, product_url):
        """
        Navigate to a product page and return the brand name.

        Args:
            product_url: URL of the product detail page

        Returns:
            Brand name in lowercase, or None if not found
        """
        self.driver.get(product_url)
        try:
            element = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, BRAND_NAME)
                )
            )
            return " ".join(element.text.lower().split())
        except Exception:
            return None