import os
import re
import requests

from playwright.sync_api import sync_playwright


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
PINCODE = os.environ.get("FIRSTCRY_PINCODE", "400059").strip()


# ============================================================
# PRODUCTS TO MONITOR
# ============================================================

PRODUCTS = [
    {
        "name": "Hot Wheels Fast & Furious Toyota Supra - Orange",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-cars-die-cast-free-wheel-premium-fast-and-furious-toyota-supra-car-for-adult-collectors-orange/24390965/product-detail",
    },
    {
        "name": "Hot Wheels Toyota GR Supra - Grey",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-free-wheel-die-cast-20-toyota-gr-supra-157-250-toy-car-grey/23074263/product-detail",
    },
    {
        "name": "Hot Wheels Color Shifters Nissan Skyline GT-R R32 - Red",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-color-shifters-nissan-skyline-gt-r-r32-car-toy-red/21252872/product-detail",
    },
    {
        "name": "Hot Wheels Ferrari LaFerrari - Yellow",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-ferrari-laferrari-5-5-die-cast-model-car-yellow/24342821/product-detail",
    },
    {
        "name": "Hot Wheels Pagani Utopia - Red",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-pagani-utopia-1-5-die-cast-red/24342822/product-detail",
    },
    {
        "name": "Hot Wheels Enzo Ferrari - Red",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-enzo-ferrari-die-cast-free-wheel-toy-car-red/24390953/product-detail",
    },
    {
        "name": "Hot Wheels Lamborghini Veneno - Black",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-lamborghini-veneno-die-cast-model-car-black/24342823/product-detail",
    },
    {
        "name": "Hot Wheels Aston Martin DBS - Green",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-aston-martin-dbs-die-cast-free-wheel-toy-car-green/24390956/product-detail",
    },
    {
        "name": "Hot Wheels Silver Series Vintage Club Lamborghini Countach LP 500 QV - White",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-1-5-silver-series-vintage-club-lamborghini-countach-lp-500-qv-die-cast-car-white/24390971/product-detail",
    },
    {
        "name": "Hot Wheels Silver Series Vintage Club Aston Martin 1963 DB5 - Blue",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-2-5-silver-series-vintage-club-aston-martin-1963-db5-die-cast-car-blue/24390970/product-detail",
    },
    {
        "name": "Hot Wheels 1989 Mercedes-Benz 560 SEC AMG Die Cast Free Wheel Toy Car - White",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-1989-mercedes-benz-560-sec-amg-die-cast-free-wheel-toy-car-white/24390955/product-detail",
    },
    {
        "name": "Hot Wheels Cars, Premium Fast & Furious Mercedes-Benz SLS AMG Coupe Black",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-cars-premium-fast-and-furious-mercedes-benz-sls-amg-coupe-black-series-serie-car-for-adult-collectors-white/24390963/product-detail",
    },
    {
        "name": "Hot Wheels Cars, Premium Fast & Furious Nissan 350Z Custom",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-cars-premium-fast-and-furious-nissan-350z-custom-personnalise-car-for-adult-collectors-black/24390962/product-detail",
    },
    {
        "name": "Hot Wheels Cars, Premium Fast & Furious McLaren 720S",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-cars-premium-fast-and-furious-mclaren-720s-car-for-adult-collectors-grey/24390964/product-detail",
    },
    {
        "name": "Hot Wheels Cars, Die-Cast Models Premium Fast & Furious Lexus LFA",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-cars-die-cast-models-premium-fast-and-furious-lexus-lfa-car-for-adult-collectors-grey/24390966/product-detail",
    },
    {
        "name": "Hot Wheels Cars, Die-Cast Models Premium Fast & Furious Lexus LFA",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-cars-die-cast-models-premium-fast-and-furious-lexus-lfa-car-for-adult-collectors-grey/24390966/product-detail",
    },
    {
        "name": "Hot Wheels 3/5 Silver Series Vintage Club 69 Copo Corvette",
        "url": "https://www.firstcry.com/hot-wheels/hot-wheels-3-5-silver-series-vintage-club-69-copo-corvette-die-cast-car-red/24390969/product-detail",
    }
]


# ============================================================
# HELPERS
# ============================================================

def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def normalize(text):
    return clean(text).lower()


def body_text(page):
    try:
        return page.locator("body").inner_text(timeout=10000)
    except Exception:
        return ""


def visible_text(page):
    return normalize(body_text(page))


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured.")
        return False

    try:
        url = (
            f"https://api.telegram.org/bot"
            f"{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "disable_web_page_preview": False,
            },
            timeout=20,
        )

        if response.ok:
            print("Telegram notification sent.")
            return True

        print(
            "Telegram error:",
            response.status_code,
            response.text[:500],
        )

    except Exception as e:
        print("Telegram exception:", e)

    return False


# ============================================================
# PRICE
# ============================================================

def extract_price(page):
    try:
        text = body_text(page)

        matches = re.findall(
            r"(?:₹|Rs\.?\s*)\s*([0-9][0-9,]*)",
            text,
            flags=re.IGNORECASE,
        )

        prices = []

        for value in matches:
            try:
                prices.append(int(value.replace(",", "")))
            except Exception:
                pass

        if prices:
            return f"₹{min(prices):,}"

    except Exception:
        pass

    return ""


# ============================================================
# PINCODE
# ============================================================

def find_pincode_input(page):
    selectors = [
        'input[placeholder="Enter Pin Code"]',
        'input[placeholder="Enter Pincode"]',
        'input[placeholder="Enter a pincode"]',
        'input[placeholder*="pincode" i]',
        'input[placeholder*="pin code" i]',
        'input[aria-label*="pincode" i]',
        'input[aria-label*="pin code" i]',
        'input[name*="pincode" i]',
        'input[id*="pincode" i]',
        'input[name*="pin" i]',
        'input[id*="pin" i]',
    ]

    for selector in selectors:
        try:
            locator = page.locator(selector)

            for i in range(min(locator.count(), 10)):
                element = locator.nth(i)

                if element.is_visible():
                    return element

        except Exception:
            continue

    # Fallback: inspect visible inputs.
    try:
        inputs = page.locator("input")

        for i in range(min(inputs.count(), 50)):
            element = inputs.nth(i)

            try:
                if not element.is_visible():
                    continue

                attributes = " ".join([
                    element.get_attribute("placeholder") or "",
                    element.get_attribute("aria-label") or "",
                    element.get_attribute("name") or "",
                    element.get_attribute("id") or "",
                ]).lower()

                if (
                    "pincode" in attributes
                    or "pin code" in attributes
                    or "postal" in attributes
                ):
                    return element

            except Exception:
                continue

    except Exception:
        pass

    return None


def open_delivery_control(page):
    patterns = [
        r"check delivery details",
        r"deliver to pincode",
        r"delivery details",
        r"change pincode",
        r"change location",
        r"select location",
        r"choose your location",
        r"delivery",
    ]

    for pattern in patterns:
        try:
            locator = page.get_by_text(
                re.compile(pattern, re.IGNORECASE)
            )

            for i in range(min(locator.count(), 10)):
                element = locator.nth(i)

                if not element.is_visible():
                    continue

                try:
                    element.click(timeout=2000)
                    page.wait_for_timeout(700)
                    return True
                except Exception:
                    continue

        except Exception:
            continue

    return False


def submit_pincode(page, input_element):
    # Look near the input first.
    for parent_level in range(1, 4):
        try:
            parent = input_element

            for _ in range(parent_level):
                parent = parent.locator("xpath=..")

            buttons = parent.locator("button, [role='button']")

            for i in range(min(buttons.count(), 20)):
                button = buttons.nth(i)

                try:
                    if not button.is_visible():
                        continue

                    text = normalize(
                        button.inner_text()
                        + " "
                        + (button.get_attribute("aria-label") or "")
                    )

                    if any(
                        word in text
                        for word in ("check", "apply", "submit", "verify")
                    ):
                        button.click(timeout=3000)
                        print(f"Clicked pincode button: {text}")
                        return True

                except Exception:
                    continue

        except Exception:
            continue

    # Search globally.
    try:
        buttons = page.locator("button, [role='button']")

        for i in range(min(buttons.count(), 200)):
            button = buttons.nth(i)

            try:
                if not button.is_visible():
                    continue

                text = normalize(
                    button.inner_text()
                    + " "
                    + (button.get_attribute("aria-label") or "")
                )

                if text.strip() in {
                    "check",
                    "apply",
                    "submit",
                    "verify",
                }:
                    button.click(timeout=3000)
                    print(f"Clicked global pincode button: {text}")
                    return True

            except Exception:
                continue

    except Exception:
        pass

    # Final fallback.
    try:
        input_element.press("Enter")
        print("Submitted pincode using Enter.")
        return True
    except Exception:
        return False


def verify_pincode(page, expected):
    expected = str(expected).strip()

    # Allow FirstCry to update delivery information.
    page.wait_for_timeout(2500)

    # 1. Visible input contains the target pincode.
    try:
        inputs = page.locator("input")

        for i in range(min(inputs.count(), 100)):
            element = inputs.nth(i)

            try:
                if not element.is_visible():
                    continue

                value = element.input_value().strip()

                if value == expected:
                    print(
                        f"Pincode {expected} is present in delivery input."
                    )
                    return True

            except Exception:
                continue

    except Exception:
        pass

    text = visible_text(page)

    # 2. Positive delivery confirmation.
    success_patterns = [
        r"delivery by",
        r"delivery on",
        r"get it by",
        r"cash on delivery",
        r"standard delivery",
        r"available for delivery",
        r"deliverable",
    ]

    for pattern in success_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print(
                f"Pincode {expected} appears accepted "
                f"(delivery information found)."
            )
            return True

    # 3. Explicit invalid/not-serviceable message.
    invalid_patterns = [
        r"please enter valid pincode",
        r"enter valid pincode",
        r"invalid pincode",
        r"invalid pin code",
        r"not serviceable",
        r"not deliverable",
        r"delivery not available",
    ]

    for pattern in invalid_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print(
                f"Pincode {expected} appears invalid/not serviceable."
            )
            return False

    # 4. Browser storage.
    try:
        storage_values = page.evaluate("""
            () => {
                const result = {};

                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    result[key] = localStorage.getItem(key);
                }

                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    result["SESSION:" + key] =
                        sessionStorage.getItem(key);
                }

                return result;
            }
        """)

        storage_text = normalize(str(storage_values))

        if expected in storage_text:
            print(
                f"Pincode {expected} found in browser storage."
            )
            return True

    except Exception:
        pass

    # 5. Do not fail merely because FirstCry did not expose a
    # confirmation message. Product-level cart verification follows.
    print(
        "Pincode confirmation text not detected. "
        "Continuing with product-level delivery/cart check."
    )

    return None


def initialize_pincode(page):
    print(f"Setting FirstCry pincode to {PINCODE}...")

    input_element = find_pincode_input(page)

    if not input_element:
        print("Pincode input not immediately visible.")
        print("Trying to open delivery/location control...")

        open_delivery_control(page)
        page.wait_for_timeout(1000)

        input_element = find_pincode_input(page)

    if not input_element:
        print("WARNING: FirstCry pincode input was not found.")
        return False

    try:
        print("Found pincode input.")

        input_element.fill("")
        input_element.fill(PINCODE)

        print(f"Entered pincode {PINCODE}.")

        if not submit_pincode(page, input_element):
            print("WARNING: Could not submit pincode.")
            return False

        verification = verify_pincode(page, PINCODE)

        if verification is False:
            print(
                f"ERROR: FirstCry explicitly rejected "
                f"pincode {PINCODE}."
            )
            return False

        if verification is True:
            print(f"Verified pincode {PINCODE}.")
        else:
            print(
                f"Pincode {PINCODE} confirmation was not explicit, "
                f"but continuing."
            )

        return True

    except Exception as e:
        print("Pincode initialization exception:", e)
        return False


# ============================================================
# STOCK DETECTION
# ============================================================

# Keep these specific. Do NOT use generic "unavailable":
# FirstCry can contain unrelated unavailable text on an
# otherwise purchasable product page.
OOS_PHRASES = [
    "out of stock",
    "out-of-stock",
    "sold out",
    "currently unavailable",
    "notify me",
    "notifyme",
]

POSITIVE_PHRASES = [
    "add to cart",
    "add to bag",
    "buy now",
]


def has_any(text, phrases):
    text = normalize(text)
    return any(normalize(phrase) in text for phrase in phrases)


def element_is_disabled(element):
    # Native disabled property.
    try:
        if element.is_disabled():
            return True
    except Exception:
        pass

    # aria-disabled.
    try:
        if (
            element.get_attribute("aria-disabled") or ""
        ).strip().lower() == "true":
            return True
    except Exception:
        pass

    # Disabled class.
    try:
        classes = (
            element.get_attribute("class") or ""
        ).lower()

        if re.search(r"\bdisabled\b", classes):
            return True
    except Exception:
        pass

    return False


def add_to_cart_is_enabled(page):
    """
    Strong availability check.

    FirstCry may render Add to Cart as:
      - button text
      - input value
      - aria-label/title
      - an element with cart-related data attributes
      - a clickable link/container

    We inspect all of these instead of relying only on inner_text().
    """

    selectors = [
        "button",
        '[role="button"]',
        'input[type="button"]',
        'input[type="submit"]',
        "a",
        "[onclick]",
        "[data-testid]",
        "[data-action]",
        "[class]",
    ]

    checked = 0

    for selector in selectors:
        try:
            elements = page.locator(selector)
            count = min(elements.count(), 300)

            for i in range(count):
                element = elements.nth(i)
                checked += 1

                try:
                    if not element.is_visible():
                        continue

                    # Collect every useful label FirstCry might expose.
                    values = []

                    for attribute in [
                        "aria-label",
                        "title",
                        "value",
                        "data-testid",
                        "data-action",
                        "data-test",
                        "name",
                        "id",
                        "class",
                    ]:
                        try:
                            value = element.get_attribute(attribute)
                            if value:
                                values.append(value)
                        except Exception:
                            pass

                    try:
                        values.append(element.inner_text())
                    except Exception:
                        pass

                    label = normalize(" ".join(values))

                    if (
                        "add to cart" not in label
                        and "add to bag" not in label
                    ):
                        continue

                    if element_is_disabled(element):
                        continue

                    print(
                        "Enabled Add to Cart/Add to Bag control found."
                    )
                    print(f"Cart control label: {label[:250]}")
                    return True

                except Exception:
                    continue

        except Exception:
            continue

    # --------------------------------------------------------
    # Text locator fallback.
    #
    # This catches cases where the visible Add to Cart text is
    # inside a nested span/div and the parent button itself has
    # no useful inner_text/attributes.
    # --------------------------------------------------------
    for phrase in ["Add to Cart", "Add to Bag"]:
        try:
            loc = page.get_by_text(
                re.compile(
                    rf"^\s*{re.escape(phrase)}\s*$",
                    re.IGNORECASE,
                )
            )

            for i in range(min(loc.count(), 20)):
                text_element = loc.nth(i)

                if not text_element.is_visible():
                    continue

                # Walk up a few levels looking for the actual clickable
                # control.
                candidate = text_element

                for _ in range(5):
                    try:
                        if (
                            candidate.is_visible()
                            and not element_is_disabled(candidate)
                        ):
                            tag = candidate.evaluate(
                                "(el) => el.tagName.toLowerCase()"
                            )

                            if tag in {
                                "button",
                                "a",
                                "input",
                            }:
                                print(
                                    "Enabled Add to Cart/Add to Bag "
                                    "found via text fallback."
                                )
                                return True

                            role = (
                                candidate.get_attribute("role")
                                or ""
                            ).lower()

                            if role == "button":
                                print(
                                    "Enabled Add to Cart/Add to Bag "
                                    "found via role fallback."
                                )
                                return True

                        candidate = candidate.locator("xpath=..")

                    except Exception:
                        break

        except Exception:
            continue

    print(
        f"No enabled Add to Cart/Add to Bag control found "
        f"after checking {checked} elements."
    )
    return False


# ============================================================
# PRODUCT CHECK
# ============================================================

def check_product(context, product):
    page = None

    try:
        page = context.new_page()

        print()
        print("=" * 70)
        print(f"Checking: {product['name']}")
        print(product["url"])
        print("=" * 70)

        page.goto(
            product["url"],
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(4500)

        pin_confirmed = initialize_pincode(page)

        # Let FirstCry refresh delivery/stock/cart state.
        page.wait_for_timeout(3000)

        body = body_text(page)
        lower_body = normalize(body)
        price = extract_price(page)

        # Never report availability if pincode was explicitly rejected
        # or the pincode could not be initialized at all.
        if pin_confirmed is False:
            print("RESULT: UNKNOWN - pincode not verified")
            return {
                "status": "unknown",
                "price": price,
            }

        # --------------------------------------------------------
        # IMPORTANT FIX:
        #
        # Check an enabled Add to Cart FIRST.
        #
        # FirstCry can contain generic words such as "unavailable"
        # elsewhere on the page. Those must never override a real,
        # enabled Add to Cart control.
        # --------------------------------------------------------
        if add_to_cart_is_enabled(page):
            print("RESULT: IN_STOCK - Add to Cart enabled")
            return {
                "status": "available",
                "price": price,
            }

        # Only after the cart check do we evaluate explicit OOS text.
        if has_any(lower_body, OOS_PHRASES):
            print("RESULT: OUT_OF_STOCK")
            return {
                "status": "out_of_stock",
                "price": price,
            }

        if has_any(lower_body, POSITIVE_PHRASES):
            print(
                "RESULT: UNKNOWN - Add to Cart text exists "
                "but enabled control was not confirmed"
            )
        else:
            print(
                "RESULT: UNKNOWN - no enabled Add to Cart "
                "and no explicit OOS signal"
            )

        return {
            "status": "unknown",
            "price": price,
        }

    except Exception as e:
        print(f"Product check failed: {e}")
        return {
            "status": "unknown",
            "price": "",
        }

    finally:
        if page:
            try:
                page.close()
            except Exception:
                pass


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("FIRSTCRY HOT WHEELS - AVAILABILITY MONITOR")
    print(f"TARGET PINCODE: {PINCODE}")
    print(f"PRODUCTS: {len(PRODUCTS)}")
    print("NO PRODUCT STATE JSON IS USED")
    print("=" * 70)

    available_products = []
    out_of_stock_count = 0
    unknown_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 1000},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        # Remove duplicate URLs while preserving order.
        seen_urls = set()
        products_to_check = []

        for product in PRODUCTS:
            if product["url"] in seen_urls:
                print(
                    f"Skipping duplicate product URL: "
                    f"{product['name']}"
                )
                continue

            seen_urls.add(product["url"])
            products_to_check.append(product)

        for product in products_to_check:
            result = check_product(context, product)
            status = result["status"]

            if status == "available":
                available_products.append({
                    **product,
                    "price": result["price"],
                })
            elif status == "out_of_stock":
                out_of_stock_count += 1
            else:
                unknown_count += 1

        browser.close()

    print()
    print("=" * 70)
    print(f"AVAILABLE: {len(available_products)}")
    print(f"OUT OF STOCK: {out_of_stock_count}")
    print(f"UNKNOWN: {unknown_count}")
    print("=" * 70)

    # --------------------------------------------------------
    # No state file:
    # Every run independently checks the products.
    # Therefore every currently available product is notified.
    # --------------------------------------------------------
    if not available_products:
        print("No products currently available.")
        return

    lines = [
        "🔥 HOT WHEELS AVAILABLE!",
        f"📍 FirstCry pincode: {PINCODE}",
        "",
    ]

    for product in available_products:
        lines.append(f"🚗 {product['name']}")

        if product["price"]:
            lines.append(f"💰 {product['price']}")

        lines.append("🛒 ADD TO CART AVAILABLE")
        lines.append(product["url"])
        lines.append("")

    send_telegram("\n".join(lines))


if __name__ == "__main__":
    main()
