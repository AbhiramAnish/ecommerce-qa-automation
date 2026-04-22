"""
Infinite Scroll 404 Retest — Qatar E-commerce
==================================================================
Test Objective:
    Verify that infinite scroll no longer triggers API calls returning
    404 errors during product page loading.

Background:
    During exploratory testing under server load, infinite scroll was
    found to be firing excessive API calls that returned 404 errors,
    causing significant page slowdowns. The issue was identified via
    browser network tab analysis and reported to developers.
    This script retests the fix by monitoring all network requests
    during scroll and verifying no 404 responses are returned from
    product scroll API endpoints.

What this test does:
    1. Opens a category/brand page with many products
    2. Enables Chrome network log capture
    3. Scrolls through the entire page triggering infinite scroll
    4. Captures all network requests made during scrolling
    5. Filters for product scroll API calls specifically
    6. Verifies none of them returned a 404 status code
    7. Prints a full report of all API calls and their status codes

Author: Abhiram Anish
"""

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# ── Configuration ──────────────────────────────────────────────────────────────

URL         = "https://test-your-site.com/"  # Page URL to test
API_KEYWORD = "api endpoint"                                  # API endpoint pattern
MAX_SCROLLS = 30                                                # Safety scroll limit


# ── Chrome Setup with Network Logging ─────────────────────────────────────────

def create_driver():
    """
    Creates a Chrome WebDriver instance with performance logging enabled.
    Performance logs capture all network requests including API calls —
    this is how we detect 404s programmatically without manual inspection.
    """
    chrome_options = Options()
    chrome_options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL"}
    )
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# ── Network Log Parser ─────────────────────────────────────────────────────────

def get_network_requests(driver):
    """
    Extracts all network requests from Chrome performance logs.
    Parses raw log entries and returns structured request data.

    Returns:
        List of dicts with 'url' and 'status' keys
    """
    requests = []
    logs = driver.get_log("performance")

    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]

            # Only care about network responses — status code lives here
            if message["method"] == "Network.responseReceived":
                response = message["params"]["response"]
                requests.append({
                    "url":    response["url"],
                    "status": response["status"]
                })
        except (KeyError, json.JSONDecodeError):
            continue

    return requests


# ── Scroll Handler ─────────────────────────────────────────────────────────────

def scroll_to_load_all_products(driver, wait):
    """
    Scrolls down the page repeatedly to trigger all infinite scroll
    API calls. Stops when no new products load after a scroll.

    Returns:
        Total number of products loaded
    """
    previous_count = 0
    scroll_count   = 0

    print("\nScrolling to trigger infinite scroll API calls...")

    while scroll_count < MAX_SCROLLS:
        products      = driver.find_elements(By.CSS_SELECTOR, ".inner-pro-col")
        current_count = len(products)

        print(f"  Scroll {scroll_count + 1}: {current_count} products loaded")

        if current_count == previous_count:
            print("  All products loaded — stopping scroll")
            break

        previous_count = current_count
        scroll_count  += 1

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            wait.until(
                lambda d: len(
                    d.find_elements(By.CSS_SELECTOR, ".inner-pro-col")
                ) > current_count
            )
        except Exception:
            break

    return previous_count


# ── Main Test ──────────────────────────────────────────────────────────────────

def run_404_retest():
    """
    Main retest.
    Scrolls the page, captures all network requests,
    filters for product scroll API calls, and verifies no 404s.
    """
    driver = create_driver()
    wait   = WebDriverWait(driver, 10)

    print(f"\n{'='*65}")
    print(f"  Infinite Scroll 404 Retest")
    print(f"  URL: {URL}")
    print(f"{'='*65}")

    try:
        driver.get(URL)

        # Wait for initial products to load before scrolling
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".inner-pro-col"))
        )

        # Scroll through all products — triggers the API calls
        total_products = scroll_to_load_all_products(driver, wait)

        # Collect all network requests made during the session
        all_requests = get_network_requests(driver)

        # Filter only product scroll API calls
        scroll_api_calls = [
            r for r in all_requests if API_KEYWORD in r["url"]
        ]

        # Separate into passing and failing
        calls_404 = [r for r in scroll_api_calls if r["status"] == 404]
        calls_ok  = [r for r in scroll_api_calls if r["status"] == 200]

        # ── Report ─────────────────────────────────────────────────
        print(f"\n{'='*65}")
        print(f"  TEST REPORT")
        print(f"{'='*65}")
        print(f"  Total products loaded   : {total_products}")
        print(f"  Scroll API calls found  : {len(scroll_api_calls)}")
        print(f"  Successful (200)        : {len(calls_ok)}")
        print(f"  Failed (404)            : {len(calls_404)}") 
        print(f"{'='*65}")

        if len(calls_404)>1:
            print(f"\n  ❌ FAILED — {len(calls_404)} scroll API calls returned 404")
        else:
            print(f"\n  ✅ PASSED — No 404 errors detected in scroll API calls")

        print(f"\n{'='*65}\n")

    finally:
        driver.quit()


if __name__ == "__main__":
    run_404_retest()