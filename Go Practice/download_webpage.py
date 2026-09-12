#!/usr/bin/env python3
"""
Navigate through multiple tests by clicking the "Next" button repeatedly, downloading
all content from a JS-rendered (Angular/SPA) site. Downloads all assets
(CSS, JS, images) and saves them in an organized timestamped folder structure for offline viewing.

This script:
1. Creates a timestamped root folder (e.g., offline_download_20260629_143052/)
2. For each grade level in FOLDER_AND_URL:
   - Creates a grade folder (e.g., grade9/)
   - For each test within that grade:
     - Creates a test folder (e.g., English Language Arts Part B: Reading/)
     - Navigates to the test URL
     - Saves each page by clicking "Next" button repeatedly
     - Downloads all assets (CSS, JS, images) into an assets/ subfolder
     - Continues until no Next button found or MAX_PAGES reached

Folder structure created:
    offline_download_20260629_143052/
    ├── _manifest.txt
    └── grade9/
        ├── English Language Arts Part B: Reading/
        │   ├── page_0001.html
        │   ├── page_0002.html
        │   └── assets/
        │       ├── style_abc123.css
        │       └── image_def456.png
        └── Mathematics Part A/
            ├── page_0001.html
            └── assets/

Usage:
    # Full installation (recommended):
    pip install playwright aiohttp aiofiles --break-system-packages
    playwright install chromium
    python3 download_webpage.py

Configuration:
    Edit FOLDER_AND_URL dictionary (line 47) to add your grade levels and tests.
    Edit MAX_PAGES, NAV_TIMEOUT_MS, and NEXT_BUTTON_SELECTOR as needed.
"""

import asyncio
import hashlib
import os
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    import aiohttp
    import aiofiles
    AIOHTTP_AVAILABLE = True
except ImportError:
    print("Warning: aiohttp and/or aiofiles not available. Assets will not be downloaded.")
    print("To enable asset downloading, install: pip install aiohttp aiofiles")
    AIOHTTP_AVAILABLE = False

from playwright.async_api import async_playwright

# Configuration: Add your grade levels and tests here
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

MAX_PAGES = 200          # safety cap so the crawl can't run forever per test
NAV_TIMEOUT_MS = 30000   # how long to wait for each page to load
WAIT_AFTER_LOAD_MS = 2000  # extra wait for SPA JS to finish rendering
SAME_DOMAIN_ONLY = True  # only download assets from the same domain

# Selectors for the Next button - will try these in order
# Based on HTML: <div class="nav-button-div"><i class="fas fa-arrow-right"></i><tra>Next</tra></div>
NEXT_BUTTON_SELECTORS = [
    "div.nav-button-div:has-text('Next')",  # Primary selector
    "div.nav-button-div >> text=Next",       # Alternative: explicit text selector
    ".nav-button-div:has-text('Next')",     # Alternative: class only
    "div:has-text('Next') >> xpath=//i[@class='fas fa-arrow-right']/..",  # More specific
]


def create_timestamped_folder() -> str:
    """Create a folder with current date and time stamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"offline_download_{timestamp}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def url_to_filename(url: str, file_type: str = "html", page_num: int = None) -> str:
    """Turn a URL into a safe, unique filename, preserving the hash route."""
    parsed = urlparse(url)
    # Keep the fragment (hash route) since that's the actual "page" for SPAs
    path_part = (parsed.path or "/") + (("#" + parsed.fragment) if parsed.fragment else "")
    safe = re.sub(r"[^a-zA-Z0-9_\-]+", "_", path_part).strip("_")
    if not safe:
        safe = "index"

    # Get file extension from URL if it's an asset
    if file_type == "asset":
        ext_match = re.search(r"\.([a-zA-Z0-9]+)(\?|$)", parsed.path)
        if ext_match:
            ext = ext_match.group(1).lower()
            # Map common extensions
            if ext in ["css", "js", "png", "jpg", "jpeg", "gif", "svg", "ico", "woff", "woff2", "ttf", "eot"]:
                safe_ext = ext
            else:
                safe_ext = "bin"
        else:
            safe_ext = "bin"
    else:
        safe_ext = "html"

    # Add page number if provided (for sequential navigation)
    if page_num is not None:
        return f"page_{page_num:04d}.{safe_ext}"

    # Add a short hash to avoid collisions from over-aggressive sanitizing
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{safe}_{h}.{safe_ext}"


def normalize_url(base: str, link: str) -> str | None:
    """Resolve a possibly-relative link against base; return None to skip."""
    if not link:
        return None
    link = link.strip()
    if link.startswith(("javascript:", "mailto:", "tel:", "#/")) is False and link.startswith("#"):
        # plain in-page anchor with no route info, skip (no new content)
        if not link.startswith("#/"):
            return None
    try:
        full = urljoin(base, link)
    except ValueError:
        return None
    return full


def same_domain(url_a: str, url_b: str) -> bool:
    return urlparse(url_a).netloc == urlparse(url_b).netloc


async def extract_assets(page, base_url: str) -> set[str]:
    """Extract all asset URLs (CSS, JS, images) from the page."""
    assets = set()
    
    # Extract CSS links
    css_links = await page.eval_on_selector_all(
        "link[rel='stylesheet']", "elements => elements.map(e => e.getAttribute('href'))"
    )
    for href in css_links:
        full = normalize_url(base_url, href)
        if full and not any(x in full for x in ["data:", "javascript:"]):
            assets.add(full)
    
    # Extract JS scripts
    js_links = await page.eval_on_selector_all(
        "script[src]", "elements => elements.map(e => e.getAttribute('src'))"
    )
    for src in js_links:
        full = normalize_url(base_url, src)
        if full and not any(x in full for x in ["data:", "javascript:"]):
            assets.add(full)
    
    # Extract images
    img_links = await page.eval_on_selector_all(
        "img[src]", "elements => elements.map(e => e.getAttribute('src'))"
    )
    for src in img_links:
        full = normalize_url(base_url, src)
        if full and not any(x in full for x in ["data:", "javascript:"]):
            assets.add(full)
    
    # Extract fonts
    font_links = await page.eval_on_selector_all(
        "link[rel*='icon'], link[rel*='preload'], link[as='font']",
        "elements => elements.map(e => e.getAttribute('href'))"
    )
    for href in font_links:
        full = normalize_url(base_url, href)
        if full and not any(x in full for x in ["data:", "javascript:"]):
            assets.add(full)
    
    return assets


async def download_asset(session, url: str, output_dir: str, asset_map: dict) -> str:
    """Download an asset and return its local filename."""
    if not AIOHTTP_AVAILABLE:
        print(f"   !! Skipping asset download (aiohttp not available): {url}")
        return None
    
    try:
        # Check if we've already downloaded this asset
        if url in asset_map:
            return asset_map[url]
        
        async with session.get(url) as response:
            if response.status == 200:
                filename = url_to_filename(url, "asset")
                filepath = os.path.join(output_dir, "assets", filename)
                
                # Ensure asset directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                content = await response.read()
                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(content)
                
                asset_map[url] = filename
                return filename
            else:
                print(f"   !! Failed to download asset {url}: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"   !! Failed to download asset {url}: {e}")
        return None


async def update_html_links(html: str, asset_map: dict) -> str:
    """Update HTML links to point to local files."""
    # This is a simplified version - a full implementation would parse the HTML properly
    # For now, we'll do basic string replacements for common patterns

    updated_html = html

    # Replace asset URLs with local paths
    for asset_url, local_filename in asset_map.items():
        if asset_url in updated_html:
            updated_html = updated_html.replace(
                asset_url,
                f"assets/{local_filename}"
            )
            # Also try with URL-encoded versions
            encoded_url = asset_url.replace('"', '%22').replace("'", '%27')
            if encoded_url in updated_html:
                updated_html = updated_html.replace(
                    encoded_url,
                    f"assets/{local_filename}"
                )

    return updated_html


def sanitize_folder_name(name: str) -> str:
    """Sanitize folder name to be filesystem-safe."""
    # Replace invalid characters with underscores
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing whitespace and dots
    safe = safe.strip('. ')
    return safe


async def download_test(page, session, start_url: str, test_folder: str, test_name: str) -> list:
    """Download all pages for a single test by clicking Next button repeatedly."""
    saved_pages = []
    asset_map = {}

    # Create assets subfolder for this test
    assets_dir = os.path.join(test_folder, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Navigate to the starting URL
    print(f"\n  [Page 1/{MAX_PAGES}] Loading test: {test_name}")
    print(f"  URL: {start_url}")
    try:
        await page.goto(start_url, timeout=NAV_TIMEOUT_MS, wait_until="networkidle")
    except Exception as e:
        print(f"   !! Failed to load start URL: {e}")
        return saved_pages

    # Give the Angular app time to finish rendering
    await page.wait_for_timeout(WAIT_AFTER_LOAD_MS)

    # Try to click Start/Begin/Continue button if present (to enter the actual test)
    print("   Checking for Start/Begin/Continue button...")
    start_button_selectors = [
        "button:has-text('Start')",
        "button:has-text('Begin')",
        "button:has-text('Start Test')",
        "button:has-text('Begin Test')",
        "button:has-text('Continue')",
        "*[role='button']:has-text('Start')",
        "div:has-text('Start')",
    ]

    for selector in start_button_selectors:
        try:
            start_btn = await page.query_selector(selector)
            if start_btn:
                is_visible = await start_btn.is_visible()
                is_enabled = await start_btn.is_enabled()
                if is_visible and is_enabled:
                    print(f"   Found Start button, clicking to begin test...")
                    await start_btn.click()
                    await page.wait_for_timeout(WAIT_AFTER_LOAD_MS)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
                    except Exception:
                        pass
                    print(f"   Entered test, now on: {page.url}")
                    break
        except Exception:
            continue

    page_num = 1

    while page_num <= MAX_PAGES:
        current_url = page.url
        print(f"   Current page: {page_num}")

        # Save the rendered HTML
        try:
            html = await page.content()
        except Exception as e:
            print(f"   !! Failed to read content: {e}")
            break

        # Extract and download assets
        print("   Extracting assets...")
        assets = await extract_assets(page, current_url)
        print(f"   Found {len(assets)} assets")

        # Download assets if aiohttp is available
        if AIOHTTP_AVAILABLE and session:
            for asset_url in assets:
                if SAME_DOMAIN_ONLY and not same_domain(asset_url, start_url):
                    continue
                if asset_url not in asset_map:
                    await download_asset(session, asset_url, test_folder, asset_map)

        # Update HTML to use local asset paths
        updated_html = await update_html_links(html, asset_map)

        # Save with sequential page numbering
        filename = url_to_filename(current_url, "html", page_num)
        filepath = os.path.join(test_folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated_html)
        saved_pages.append((page_num, current_url, filename))
        print(f"   -> saved as {filename}")

        # Look for the Next button - try multiple selectors
        try:
            next_button = None
            used_selector = None

            # Try each selector in order
            for selector in NEXT_BUTTON_SELECTORS:
                try:
                    next_button = await page.query_selector(selector)
                    if next_button:
                        used_selector = selector
                        break
                except Exception:
                    # If one selector fails, try the next
                    continue

            if next_button:
                # Check if button is visible and enabled
                is_visible = await next_button.is_visible()
                is_enabled = await next_button.is_enabled()

                if is_visible and is_enabled:
                    print(f"   Found Next button (using selector: {used_selector[:50]}...), clicking...")

                    # Click the Next button
                    await next_button.click()

                    # Wait for navigation/content to load
                    await page.wait_for_timeout(WAIT_AFTER_LOAD_MS)

                    # Wait for network to be idle (new content loaded)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
                    except Exception:
                        # If networkidle times out, continue anyway
                        pass

                    page_num += 1
                else:
                    print(f"   Next button not clickable (visible={is_visible}, enabled={is_enabled})")
                    print("   Reached end of test.")
                    break
            else:
                print("   No Next button found with any selector. Reached end of test.")
                print(f"   Tried selectors: {len(NEXT_BUTTON_SELECTORS)}")
                break

        except Exception as e:
            print(f"   !! Error while looking for/clicking Next button: {e}")
            break

    print(f"  Completed: {test_name} - Downloaded {len(saved_pages)} page(s)\n")
    return saved_pages


async def crawl():
    # Create timestamped output directory
    base_output_dir = create_timestamped_folder()
    print(f"=" * 80)
    print(f"STARTING DOWNLOAD")
    print(f"=" * 80)
    print(f"Output directory: {os.path.abspath(base_output_dir)}\n")

    all_tests_info = {}  # Store info for manifest

    # Create HTTP session for downloading assets if available
    if AIOHTTP_AVAILABLE:
        connector = aiohttp.TCPConnector(limit=10)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        if AIOHTTP_AVAILABLE:
            session_context = aiohttp.ClientSession(connector=connector)
            session = await session_context.__aenter__()
        else:
            session = None

        # Iterate through each grade level
        for grade_level, tests in FOLDER_AND_URL.items():
            print(f"\n{'=' * 80}")
            print(f"Processing: {grade_level.upper()}")
            print(f"{'=' * 80}")

            # Create grade level folder
            grade_folder = os.path.join(base_output_dir, sanitize_folder_name(grade_level))
            os.makedirs(grade_folder, exist_ok=True)

            all_tests_info[grade_level] = {}

            # Iterate through each test
            for test_name, test_url in tests.items():
                print(f"\n--- Test: {test_name} ---")

                # Create test folder
                test_folder = os.path.join(grade_folder, sanitize_folder_name(test_name))
                os.makedirs(test_folder, exist_ok=True)

                # Download all pages for this test
                saved_pages = await download_test(page, session, test_url, test_folder, test_name)

                # Store test info
                all_tests_info[grade_level][test_name] = {
                    'url': test_url,
                    'folder': test_folder,
                    'pages': saved_pages
                }

        await browser.close()

        # Close aiohttp session if it was opened
        if AIOHTTP_AVAILABLE:
            await session_context.__aexit__(None, None, None)

    # Write a comprehensive manifest
    manifest_path = os.path.join(base_output_dir, "_manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(f"Offline Download Archive\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Navigation Method: Sequential (Next button clicking)\n")
        f.write(f"Asset downloading: {'ENABLED' if AIOHTTP_AVAILABLE else 'DISABLED (install aiohttp)'}\n")
        f.write(f"\n" + "="*80 + "\n\n")

        total_pages = 0
        for grade_level, tests in all_tests_info.items():
            f.write(f"GRADE LEVEL: {grade_level}\n")
            f.write("="*80 + "\n\n")

            for test_name, test_info in tests.items():
                f.write(f"  Test: {test_name}\n")
                f.write(f"  URL: {test_info['url']}\n")
                f.write(f"  Folder: {os.path.relpath(test_info['folder'], base_output_dir)}\n")
                f.write(f"  Pages: {len(test_info['pages'])}\n")

                if test_info['pages']:
                    f.write(f"  Files:\n")
                    for _, _, filename in test_info['pages']:
                        f.write(f"    - {filename}\n")
                        total_pages += 1

                f.write("\n")

            f.write("\n")

        f.write(f"=" * 80 + "\n")
        f.write(f"SUMMARY\n")
        f.write(f"=" * 80 + "\n")
        f.write(f"Total grade levels: {len(all_tests_info)}\n")
        total_tests = sum(len(tests) for tests in all_tests_info.values())
        f.write(f"Total tests: {total_tests}\n")
        f.write(f"Total pages: {total_pages}\n")
        f.write(f"\n" + "="*80 + "\n\n")
        f.write("INSTRUCTIONS FOR OFFLINE VIEWING:\n")
        f.write("="*80 + "\n")
        f.write("1. Navigate to the grade level folder (e.g., grade9/)\n")
        f.write("2. Open the test folder you want to view\n")
        f.write("3. Open page_0001.html to start from the beginning\n")
        f.write("4. Pages are numbered sequentially (page_0001.html, page_0002.html, etc.)\n")
        if AIOHTTP_AVAILABLE:
            f.write("5. All assets (CSS, JS, images) are stored in the 'assets' subfolder within each test folder\n")
        else:
            f.write("5. Assets were not downloaded (install aiohttp + aiofiles for asset support)\n")

    print(f"\n" + "="*80)
    print(f"DOWNLOAD COMPLETE")
    print(f"="*80)
    print(f"Output directory: {os.path.abspath(base_output_dir)}")
    total_tests = sum(len(tests) for tests in all_tests_info.values())
    total_pages = sum(len(test_info['pages']) for tests in all_tests_info.values() for test_info in tests.values())
    print(f"Downloaded {total_tests} test(s) with {total_pages} total page(s).")
    print(f"\nFolder structure:")
    for grade_level, tests in all_tests_info.items():
        print(f"  {grade_level}/")
        for test_name, test_info in tests.items():
            page_count = len(test_info['pages'])
            print(f"    {sanitize_folder_name(test_name)}/ ({page_count} pages)")
    print(f"\nTo view offline:")
    print(f"1. Navigate to {base_output_dir}")
    print(f"2. Browse to grade level > test folder")
    print(f"3. Open page_0001.html in your browser")
    print(f"4. Check _manifest.txt for the complete file list")
    print(f"="*80)


if __name__ == "__main__":
    asyncio.run(crawl())