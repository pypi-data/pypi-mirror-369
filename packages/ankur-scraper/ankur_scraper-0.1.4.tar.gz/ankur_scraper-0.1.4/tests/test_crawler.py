# tests/test_crawler.py

from urllib.parse import urlparse
from core.crawler import get_internal_links
import tldextract

def is_same_domain(base_url, link_url):
    """Helper to check if a link is in the same domain"""
    base = tldextract.extract(base_url)
    link = tldextract.extract(link_url)
    return base.domain == link.domain and base.suffix == link.suffix

def test_get_internal_links_simple_site():
    base_url = "https://www.pinecone.io"
    links = get_internal_links(base_url, max_depth=1)

    assert isinstance(links, set) or isinstance(links, list)
    assert len(links) > 0, "Should return at least one internal link"

    # Ensure all links are in the same domain
    for link in links:
        assert is_same_domain(base_url, link), f"External link found: {link}"
        assert link.startswith("http"), f"Invalid link format: {link}"
        assert urlparse(link).netloc == urlparse(base_url).netloc, f"Link {link} is not internal to {base_url}"
