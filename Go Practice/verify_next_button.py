#!/usr/bin/env python3
"""
Verify Next button selector across all test URLs
"""
import asyncio
from playwright.async_api import async_playwright

# Same URLs from download_webpage.py
FOLDER_AND_URL = {
    "grade9": {
        "English Language Arts Part A: Writing": "https://abed.vretta.com/#/en/test-auth/shared-test-version/628/6690",
        "English Language Arts Part B: Reading": "https://abed.vretta.com/#/en/test-auth/shared-test-version/629/6833",
        "Mathematics Part A": "https://abed.vretta.com/#/en/test-auth/shared-test-version/646/7094",
        "Mathematics Part B": "https://abed.vretta.com/#/en/test-auth/shared-test-version/647/7015",
        "Knowledge and Eployability Science": "https://abed.vretta.com/#/en/test-auth/shared-test-version/435/6364",
        "Practice test Science": "https://abed.vretta.com/#/en/test-auth/shared-test-version/434/6803",
        "Science 9 Unit Practice Test Biological Diversity": "https://abed.vretta.com/#/en/test-auth/shared-test-version/959/7051",
        "Science 9 Unit Practice Test Matter & Chemical Change": "https://abed.vretta.com/#/en/test-auth/shared-test-version/952/7148",
        "Science 9 Unit Practice Test Environmental Chemistry": "https://abed.vretta.com/#/en/test-auth/shared-test-version/988/7238",
        "Science 9 Unit Practice Test Electrical Principles & Technologies": "https://abed.vretta.com/#/en/test-auth/shared-test-version/990/7231",
        "Science 9 Unit Practice Test Space Exploration": "https://abed.vretta.com/#/en/test-auth/shared-test-version/1012/7226",
        "Social Studies 9": "https://abed.vretta.com/#/en/test-auth/shared-test-version/637/6835",
    }
}

SELECTORS_TO_TEST = [
    "div.nav-button-div:has-text('Next')",
    "div.nav-button-div >> text=Next",
    ".nav-button-div:has-text('Next')",
    "div.nav-button-div",
    ".nav-button-div",
]

async def verify_selectors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        results = {}

        for grade_level, tests in FOLDER_AND_URL.items():
            print(f"\n{'=' * 80}")
            print(f"Grade Level: {grade_level}")
            print(f"{'=' * 80}")

            for test_name, url in tests.items():
                print(f"\nTest: {test_name}")
                print(f"URL: {url}")

                try:
                    # Navigate to the page
                    await page.goto(url, timeout=30000, wait_until="networkidle")
                    await page.wait_for_timeout(2000)  # Wait for Angular to render

                    test_results = {
                        'url': url,
                        'selectors': {},
                        'next_button_html': None
                    }

                    # Test each selector
                    for selector in SELECTORS_TO_TEST:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                is_visible = await element.is_visible()
                                is_enabled = await element.is_enabled()
                                test_results['selectors'][selector] = {
                                    'found': True,
                                    'visible': is_visible,
                                    'enabled': is_enabled
                                }
                                print(f"  ✓ Selector: {selector}")
                                print(f"    - Visible: {is_visible}, Enabled: {is_enabled}")
                            else:
                                test_results['selectors'][selector] = {'found': False}
                                print(f"  ✗ Selector: {selector} - NOT FOUND")
                        except Exception as e:
                            test_results['selectors'][selector] = {'found': False, 'error': str(e)}
                            print(f"  ✗ Selector: {selector} - ERROR: {e}")

                    # Get HTML of the Next button if found
                    try:
                        next_div = await page.query_selector("div.nav-button-div")
                        if next_div:
                            html = await next_div.evaluate("el => el.outerHTML")
                            test_results['next_button_html'] = html
                            print(f"\n  Next button HTML:")
                            print(f"  {html[:200]}...")
                    except Exception as e:
                        print(f"  Could not get Next button HTML: {e}")

                    # Try to find all divs with 'Next' text
                    try:
                        all_next_elements = await page.query_selector_all("*:has-text('Next')")
                        print(f"\n  Found {len(all_next_elements)} elements containing 'Next'")

                        # Get HTML of first few
                        for i, elem in enumerate(all_next_elements[:3]):
                            tag = await elem.evaluate("el => el.tagName")
                            classes = await elem.evaluate("el => el.className")
                            print(f"    Element {i+1}: <{tag}> class='{classes}'")
                    except Exception as e:
                        print(f"  Error finding Next elements: {e}")

                    results[test_name] = test_results

                except Exception as e:
                    print(f"  !! Failed to load page: {e}")
                    results[test_name] = {'error': str(e)}

        await browser.close()

        # Summary
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")

        for test_name, test_result in results.items():
            if 'error' in test_result and 'selectors' not in test_result:
                print(f"\n{test_name}: FAILED TO LOAD")
            else:
                print(f"\n{test_name}:")
                working_selectors = [s for s, r in test_result['selectors'].items()
                                   if r.get('found') and r.get('visible') and r.get('enabled')]
                if working_selectors:
                    print(f"  ✓ Working selectors: {len(working_selectors)}")
                    for s in working_selectors:
                        print(f"    - {s}")
                else:
                    print(f"  ✗ No working selectors found")

if __name__ == "__main__":
    asyncio.run(verify_selectors())
