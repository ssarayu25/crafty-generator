from playwright.sync_api import sync_playwright
import os, requests

def scrape_yarnspirations(max_pages=None):
    os.makedirs("scraped_patterns", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)    # you can set headless=True later
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # start at page 1
        url = "https://www.yarnspirations.com/collections/patterns"
        page_index = 1

        while True:
            print(f"\n📄 === Scraping page {page_index}: {url} ===")
            page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            page.screenshot(path=f"navigation_debug_page{page_index}.png")
            print(f"Navigation complete. Screenshot saved as navigation_debug_page{page_index}.png.")

            # ────────────────────────────────────────────────────────────────────────────
            # YOUR ORIGINAL POPUP-CLOSING CODE (UNCHANGED)
            # ────────────────────────────────────────────────────────────────────────────
            try:
                cookie_btn = page.locator("button:has-text('Accept and Close')")
                if cookie_btn.is_visible(timeout=5000):
                    cookie_btn.click()
                    print("✅ Cookie banner closed")
            except:
                print("ℹ️ No cookie banner detected")

            # give promo popup time to appear
            page.wait_for_timeout(10000)

            try:
                svg_close_button = page.wait_for_selector(
                    "svg path[style*='cursor: pointer']",
                    timeout=10000
                )
                if svg_close_button:
                    svg_close_button.click()
                    print("✅ SVG-based promotional popup closed.")
            except Exception as e:
                print("ℹ️ No SVG-based promotional popup detected or error while closing it:", e)

            # close mail-chimp / generic modals
            for sel in [
                "div#mc-popin button[aria-label='Close']",
                "button:has-text('×')",
                ".modal__close"
            ]:
                try:
                    btn = page.locator(sel)
                    if btn.first.is_visible(timeout=5000):
                        btn.first.click()
                        print(f"✅ Closed promo popup via selector {sel}")
                        break
                except:
                    pass

            try:
                promo_popup_close_button = page.locator("button[aria-label='Close']")
                if promo_popup_close_button.is_visible(timeout=5000):
                    promo_popup_close_button.click()
                    print("✅ Promotional popup closed.")
            except Exception as e:
                print("ℹ️ No promotional popup detected or error while closing it:", e)

            # ────────────────────────────────────────────────────────────────────────────
            # SCROLL UNTIL DOWNLOAD BUTTONS APPEAR
            # ────────────────────────────────────────────────────────────────────────────
            max_scrolls = 15
            for i in range(max_scrolls):
                btns = page.locator("a.download-pattern-btn")
                count = btns.count()
                if count > 0:
                    print(f"✅ Found {count} download buttons on scroll #{i+1}")
                    break
                print(f"🔄 Scrolling attempt #{i+1}")
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
            else:
                print("⚠️ No download buttons found on this page.")
                btns = page.locator("a.download-pattern-btn")  # will be zero

            # ────────────────────────────────────────────────────────────────────────────
            # DOWNLOAD EACH PDF VIA HTTP GET
            # ────────────────────────────────────────────────────────────────────────────
            for idx in range(btns.count()):
                href = btns.nth(idx).get_attribute("href")
                if not href:
                    continue
                filename = href.split("/")[-1].split("?")[0]
                save_path = os.path.join("scraped_patterns", filename)
                if os.path.exists(save_path):
                    print(f"🔁 {filename} already exists, skipping")
                    continue

                retries = 3
                for attempt in range(retries):
                    try:
                        resp = requests.get(href, stream=True, timeout=30)  # Increased timeout to 30 seconds
                        resp.raise_for_status()
                        with open(save_path, "wb") as f:
                            for chunk in resp.iter_content(1024):
                                f.write(chunk)
                        print(f"✅ Saved {filename}")
                        break  # Exit retry loop on success
                    except requests.exceptions.RequestException as e:
                        print(f"⚠️ Attempt {attempt + 1} failed for {filename}: {e}")
                        if attempt == retries - 1:
                            print(f"❌ Skipping {filename} after {retries} attempts.")
                            with open("failed_downloads.log", "a") as log_file:
                                log_file.write(f"{href}\n")

            # ────────────────────────────────────────────────────────────────────────────
            # HANDLE PAGINATION (NEXT PAGE)
            # ────────────────────────────────────────────────────────────────────────────
            if max_pages and page_index >= max_pages:
                print(f"Reached max_pages={max_pages}, stopping.")
                break

            next_el = page.locator("a[aria-label='Page Next']").first
            if not next_el.count():
                print("🏁 No Next button found—scraping complete.")
                break

            next_href = next_el.get_attribute("href")
            if not next_href:
                print("⚠️ Next button had no href—stopping.")
                break

            url = next_href
            page_index += 1

        print("🎉 All downloads complete!")

        browser.close()

if __name__ == "__main__":
    scrape_yarnspirations(max_pages=200)  # or None to go until the very last page
    print("🎉 Done!")