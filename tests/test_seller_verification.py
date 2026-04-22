"""
Seller Verification Test — Qatar E-commerce
=============================================
Test Objective:
    Verify that all products listed under a seller page belong
    to the expected seller.

Background:
    During exploratory testing, products from incorrect sellers
    were found appearing on a seller's dedicated page.
    This test systematically verifies seller correctness across
    all subcategories to catch this class of bug automatically.

What this test does:
    1. Navigates to a seller page
    2. Iterates through all subcategory filters
    3. Loads all products via infinite scroll in each subcategory
    4. Visits each product page and verifies the seller name
    5. Reports any mismatches with product URL and actual seller found

Author: Abhiram Anish
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pages.product_listing_page import ProductListingPage, CATEGORY_FILTER


# ── Configuration ──────────────────────────────────────────────────────────────

URL             = "https://test-your-site.com/"  # Seller page URL
EXPECTED_SELLER = "expected seller name"                         # Expected seller
WAIT_TIMEOUT    = 3                                              # seconds


# ── Main Test ──────────────────────────────────────────────────────────────────

def run_seller_verification_test():
    """
    Iterates all subcategories on the seller page, loads all products
    via infinite scroll, and verifies seller correctness on each product page.
    """
    bugs=0
    total_products=0
    driver = webdriver.Chrome()
    wait   = WebDriverWait(driver, WAIT_TIMEOUT)
    page   = ProductListingPage(driver, wait)

    print(f"\n{'='*60}")
    print(f"  Seller Verification Test")
    print(f"  URL            : {URL}")
    print(f"  Expected Seller: {EXPECTED_SELLER}")
    print(f"{'='*60}\n")

    try:
        page.open(URL)

        # Get total subcategory filters
        subcategories = page.get_filters(CATEGORY_FILTER)
        total = len(subcategories)
        print(f"Total subcategories found: {total}\n")

        for i in range(total):

            # Re-open and re-fetch to avoid stale element references
            page.open(URL)
            subcategories = page.get_filters(CATEGORY_FILTER)

            subcat = subcategories[i]

            # Get subcategory name from data-subcat_name and brand from data_bname data attribute
            name = page.get_filter_name(subcat,CATEGORY_FILTER)
            print(f"\n[Category {i+1}/{total}] {name}")

            # Click the subcategory filter
            page.click_filter(subcat)

            # Load all products via infinite scroll
            page.scroll_to_load_all_products()

            # Collect all product links
            links = page.get_product_links()
            print(f"Products found: {len(links)}")
            total_products=total_products+len(links)

            # Verify seller on each product page
            for link in links:
                actual_seller = page.get_seller_name(link)

                if actual_seller is None:
                    print(f"  [INFO] Seller info missing (out of stock?): {link}")
                    continue

                if EXPECTED_SELLER.lower() not in actual_seller:
                    print(f"\n  [BUG FOUND] Wrong seller!")
                    print(f"  Product URL : {link}")
                    print(f"  Expected    : {EXPECTED_SELLER}")
                    print(f"  Found       : {actual_seller}")
                    bugs=bugs+1

    finally:
        driver.quit()
        print(f"\n{'='*60}")
        print("  Test Complete\n")
        print(f"  Total bugs : {bugs}")
        print(f"  Total Products Checked : {total_products}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    run_seller_verification_test()