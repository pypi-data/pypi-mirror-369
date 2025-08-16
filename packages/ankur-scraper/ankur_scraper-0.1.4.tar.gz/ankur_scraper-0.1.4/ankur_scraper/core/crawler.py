# ankur_scraper/core/crawler.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
from collections import deque
from ankur_scraper.logging_config import get_logger

info_logger = get_logger("info")
error_logger = get_logger("error")

IGNORED_SCHEMES = ("mailto:", "tel:", "javascript:")
IGNORED_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".svg", ".gif", ".zip", ".doc", ".docx", ".mp4", ".mp3")

def is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and not url.startswith(IGNORED_SCHEMES)

def is_internal_link(base_url: str, link_url: str) -> bool:
    return urlparse(base_url).netloc == urlparse(link_url).netloc

def should_ignore_url(url: str) -> bool:
    if any(url.lower().startswith(scheme) for scheme in IGNORED_SCHEMES):
        return True
    if any(url.lower().endswith(ext) for ext in IGNORED_EXTENSIONS):
        return True
    if url.strip() in ("#", ""):
        return True
    return False

def normalize_url(href: str, base_url: str) -> str:
    return urljoin(base_url, href).split("#")[0]  # remove fragment

def get_internal_links(base_url: str, max_depth: int = 1, user_agent: str = "Mozilla/5.0") -> set:
    visited = set()
    queue = deque([(base_url, 0)])
    headers = {"User-Agent": user_agent}

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited or depth > max_depth:
            continue

        visited.add(current_url)

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "lxml")
            for link_tag in soup.find_all("a", href=True):
                href = link_tag["href"]
                if should_ignore_url(href):
                    continue

                normalized = normalize_url(href, current_url)
                if is_valid_http_url(normalized) and is_internal_link(base_url, normalized):
                    if normalized not in visited:
                        queue.append((normalized, depth + 1))

        except requests.RequestException as e:
            error_logger.error(f"Failed to fetch {current_url}: {str(e)}")

    info_logger.info(f"Found {len(visited)} internal links from {base_url}")
    return visited
