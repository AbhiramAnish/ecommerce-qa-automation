# Ecommerce QA Automation Suite — Selenium

Automated test suite for a live Qatar-based ecommerce platform covering seller integrity verification and infinite scroll API monitoring.

Built with **Selenium WebDriver** and **Page Object Model (POM)** design pattern.

---

## 📁 Project Structure

```
ecommerce-qa-automation/
│
├── pages/
│   └── product_listing_page.py        # Page Object Model — reusable page interactions
│
├── tests/
│   ├── test_seller_verification.py    # Seller integrity verification test
│   └── test_scroll_404_regression.py  # Infinite scroll 404 retest
│
├── requirements.txt                   # Python dependencies
└── README.md
```

---

## 🐛 Bugs These Tests Were Built to Catch

### Bug 1 — Seller Integrity Defect
During exploratory testing on seller pages, products from **incorrect sellers** were found appearing on a seller's dedicated page — some listings showed a **different seller name** than the page they belonged to.

### Bug 2 — Infinite Scroll 404 Errors
During exploratory testing under server load, infinite scroll was firing excessive API calls returning **404 errors**, causing significant page slowdowns. Identified and documented via browser network tab analysis, reported to developers.

---

## Test 1 — Seller Verification

### What it does

```
Seller Page
    │
    ├── Subcategory 1
    │       ├── Infinite scroll → load all products
    │       ├── Product 1 → verify seller ✅ or ❌
    │       ├── Product 2 → verify seller ✅ or ❌
    │       └── ...
    │
    ├── Subcategory 2
    │       └── ...
    │
    └── Subcategory N
            └── ...
```

1. Navigates to a seller page
2. Detects all subcategory filters dynamically
3. Clicks each filter and waits for navigation
4. Handles infinite scroll to load all products
5. Visits each product page and verifies seller name matches expected value
6. Reports mismatches with product URL and actual seller found

### Key Technical Challenges Solved

| Challenge | Solution |
|-----------|----------|
| Infinite scroll product loading | Scroll loop with dynamic product count comparison |
| Stale element references after navigation | Re-fetch elements after each page reload |
| Dynamic URL change detection | `wait.until` lambda checking URL change |
| JavaScript-rendered click targets | `execute_script` for scroll into view and click |
| Flaky element waits | `WebDriverWait` with `expected_conditions` throughout |

### Sample Output

```
============================================================
  Seller Verification Test
  URL            : https://your-ecommerce-site.com/seller/...
  Expected Seller: express way trading
============================================================

Total subcategories found: 8

[Subcategory 1/8] Electronics
Products found: 12

[Subcategory 2/8] Kitchen Appliances
Products found: 34

  [BUG FOUND] Wrong seller!
  Product URL : https://your-ecommerce-site.com/product/xyz
  Expected    : express way trading
  Found       : some other seller

============================================================
  Test Complete
============================================================
```

### Configuration

```python
URL             = "https://your-ecommerce-site.com/seller/..."
EXPECTED_SELLER = "express way trading"
WAIT_TIMEOUT    = 5
```

### Run

```bash
python tests/test_seller_verification.py
```

---

## Test 2 — Infinite Scroll 404 Retest

### What it does

```
Open category page
    │
    ├── Enable Chrome network log capture
    │
    ├── Scroll → Scroll → Scroll (infinite scroll triggered)
    │       └── All product_scroll API calls captured in background
    │
    └── Verify: Zero 404 responses in scroll API calls
            ├── PASS ✅ — fix is holding
            └── FAIL ❌ — bug has returned
```

### How Network Monitoring Works

Standard Selenium cannot read network responses directly. This test uses **Chrome Performance Logs** — a built-in Chrome capability that records all network activity during the session.

```python
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
```

After scrolling, all log entries are parsed and filtered for `product_scroll` API calls — the exact endpoints responsible for loading products during infinite scroll.

### Sample Output

```
=================================================================
  Infinite Scroll 404 Retest
  URL: https://your-ecommerce-site.com/category-page
=================================================================

Scrolling to trigger infinite scroll API calls...
  Scroll 1: 30 products loaded
  Scroll 2: 60 products loaded
  Scroll 3: 90 products loaded
  All products loaded — stopping scroll

=================================================================
  TEST REPORT
=================================================================
  Total products loaded   : 90
  Scroll API calls found  : 6
  Successful (200)        : 6
  Failed (404)            : 0
=================================================================

  ✅ PASSED — No 404 errors detected in scroll API calls
```

### Configuration

```python
URL         = "https://your-ecommerce-site.com/category-page"
API_KEYWORD = "product_scroll"
MAX_SCROLLS = 30
```

### Run

```bash
python tests/test_scroll_404_regression.py
```

---

## Page Object Model

`pages/product_listing_page.py` is reusable across all listing page types — seller, brand, category, subcategory — since they all share the same structure on this platform.

| Method | Description |
|--------|-------------|
| `open(url)` | Navigate to any listing page |
| `get_filters(selector)` | Fetch all filter buttons dynamically |
| `get_filter_name(element, attribute)` | Extract filter display name |
| `click_filter(element)` | Scroll into view and click filter |
| `scroll_to_load_all_products()` | Handle infinite scroll until all products load |
| `get_product_links()` | Collect all product URLs on current page |
| `get_seller_name(url)` | Visit product page and return seller name |
| `get_brand_name(url)` | Visit product page and return brand name |

---

## Tech Stack

- **Language:** Python 3.x
- **Automation:** Selenium WebDriver 4.x
- **Design Pattern:** Page Object Model (POM)
- **Network Monitoring:** Chrome Performance Logs
- **Browser:** Google Chrome + ChromeDriver
- **Waiting Strategy:** Explicit waits (`WebDriverWait` + `expected_conditions`)

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/AbhiramAnish/ecommerce-qa-automation.git
cd ecommerce-qa-automation
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run tests
```bash
python tests/test_seller_verification.py
python tests/test_scroll_404_regression.py
```

> Make sure Google Chrome is installed. ChromeDriver is managed automatically.

---

## Author

**Abhiram Anish**
- 🔗 [LinkedIn](https://linkedin.com/in/abhiramanish)
- 🐙 [GitHub](https://github.com/AbhiramAnish)