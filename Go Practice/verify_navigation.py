#!/usr/bin/env python3
"""
Investigate navigation buttons on test pages
"""
import asyncio
from playwright.async_api import async_playwright

FOLDER_AND_URL = {
    "grade9": {
        "English Language Arts Part A: Writing": "https://abed.vretta.com/#/en/test-auth/shared-test-version/628/6690",
        "English Language Arts Part B: Reading": "https://abed.vretta.com/#/en/test-auth/shared-test-version/629/6833",
        "Mathematics Part A": "https://abed.vretta.com/#/en/test-auth/shared-test-version/646/7094",
        "Mathematics Part B": "https://abed.vretta.com/#/en/test-auth/shared-test-version/647/7015",
    }
}

async def investigate_navigation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for grade_level, tests in FOLDER_AND_URL.items():
            for test_name, url in list(tests.items())[:2]:  # Just check first 2 tests
                print(f"\n{'=' * 80}")
                print(f"Test: {test_name}")
                print(f"URL: {url}")
                print(f"{'=' * 80}")

                try:
                    await page.goto(url, timeout=30000, wait_until="networkidle")
                    await page.wait_for_timeout(3000)

                    # Look for common navigation buttons
                    print("\n1. Looking for buttons with common text...")
                    button_texts = ['Start', 'Begin', 'Next', 'Continue', 'Submit', 'Start Test', 'Begin Test']

                    for text in button_texts:
                        elements = await page.query_selector_all(f"button:has-text('{text}')")
                        if elements:
                            print(f"  ✓ Found {len(elements)} button(s) with text: '{text}'")
                            for i, elem in enumerate(elements[:2]):
                                html = await elem.evaluate("el => el.outerHTML")
                                is_visible = await elem.is_visible()
                                print(f"    Button {i+1} (visible={is_visible}): {html[:150]}...")

                    # Look for all buttons
                    print("\n2. Finding all visible buttons...")
                    all_buttons = await page.query_selector_all("button")
                    visible_buttons = []
                    for btn in all_buttons:
                        is_visible = await btn.is_visible()
                        if is_visible:
                            visible_buttons.append(btn)

                    print(f"  Found {len(visible_buttons)} visible buttons")
                    for i, btn in enumerate(visible_buttons[:5]):
                        text = await btn.inner_text()
                        html = await btn.evaluate("el => el.outerHTML")
                        print(f"  Button {i+1}: '{text.strip()}' - {html[:100]}...")

                    # Look for nav-button-div elements
                    print("\n3. Looking for nav-button-div elements...")
                    nav_divs = await page.query_selector_all("div.nav-button-div")
                    if nav_divs:
                        print(f"  Found {len(nav_divs)} nav-button-div element(s)")
                        for i, div in enumerate(nav_divs):
                            html = await div.evaluate("el => el.outerHTML")
                            is_visible = await div.is_visible()
                            text = await div.inner_text()
                            print(f"  Div {i+1} (visible={is_visible}): '{text.strip()}' - {html[:150]}...")
                    else:
                        print("  No nav-button-div elements found")

                    # Look for clickable divs with navigation text
                    print("\n4. Looking for clickable divs with navigation text...")
                    for text in ['Start', 'Next', 'Continue', 'Begin']:
                        divs = await page.query_selector_all(f"div:has-text('{text}')")
                        clickable = []
                        for div in divs[:5]:
                            is_visible = await div.is_visible()
                            if is_visible:
                                clickable.append(div)

                        if clickable:
                            print(f"  Found {len(clickable)} visible div(s) with text: '{text}'")

                    # Try clicking Start button if exists
                    print("\n5. Attempting to click Start button...")
                    start_selectors = [
                        "button:has-text('Start')",
                        "button:has-text('Begin')",
                        "button:has-text('Start Test')",
                        "*[role='button']:has-text('Start')",
                    ]

                    started = False
                    for selector in start_selectors:
                        try:
                            start_btn = await page.query_selector(selector)
                            if start_btn:
                                is_visible = await start_btn.is_visible()
                                if is_visible:
                                    print(f"  Clicking: {selector}")
                                    await start_btn.click()
                                    await page.wait_for_timeout(3000)
                                    started = True
                                    break
                        except Exception as e:
                            continue

                    if started:
                        print("\n6. After clicking Start, checking for Next button...")
                        next_selectors = [
                            "div.nav-button-div:has-text('Next')",
                            "button:has-text('Next')",
                            ".nav-button-div:has-text('Next')",
                        ]

                        for selector in next_selectors:
                            try:
                                next_btn = await page.query_selector(selector)
                                if next_btn:
                                    is_visible = await next_btn.is_visible()
                                    html = await next_btn.evaluate("el => el.outerHTML")
                                    print(f"  ✓ Found Next button with: {selector}")
                                    print(f"    Visible: {is_visible}")
                                    print(f"    HTML: {html[:150]}...")
                            except Exception as e:
                                continue

                    # Take a screenshot
                    screenshot_path = f"/home/tran-gia/Documents/2026_coding/Coding interview/Go Practice/screenshot_{test_name[:30].replace(' ', '_')}.png"
                    await page.screenshot(path=screenshot_path)
                    print(f"\n  Screenshot saved: {screenshot_path}")

                except Exception as e:
                    print(f"  !! Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(investigate_navigation())
