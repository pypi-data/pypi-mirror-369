# ankur_scraper/core/page_scraper.py

import httpx
from ankur_scraper.core.html_extractor import extract_text_sections
from playwright.sync_api import sync_playwright
from ankur_scraper.logging_config import get_logger

info_logger = get_logger("info")
error_logger = get_logger("error")


def fetch_static_html(url, timeout=10, headers=None):
    """Try to fetch HTML using httpx."""
    try:
        resp = httpx.get(url, timeout=timeout, headers=headers)
        if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
            return resp.text
    except Exception:
        pass
    return None


def fetch_dynamic_html(url, timeout=15, user_agent=None):
    """Render page using Playwright headless browser."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent or "AnkurScraperBot/1.0")
            page = context.new_page()
            page.set_default_navigation_timeout(timeout * 1000)
            page.goto(url)
            html = page.content()
            browser.close()
            return html
    except Exception:
        return None


def scrape_page(url, use_dynamic=False, timeout=10):
    info_logger.info(f"Scraping page: {url} (use_dynamic={use_dynamic})")
    headers = {
        "User-Agent": "AnkurScraperBot/1.0"
    }

    html = fetch_static_html(url, timeout=timeout, headers=headers)

    if html is None and use_dynamic:
        html = fetch_dynamic_html(url, timeout=timeout, user_agent=headers["User-Agent"])

    if html:
        info_logger.info(f"Successfully fetched HTML for {url}")
         # Extract sections from the HTML content
        return extract_text_sections(html)
    else:
        error_logger.error(f"Failed to fetch HTML for {url}")
        raise Exception("Failed to load HTML content")
