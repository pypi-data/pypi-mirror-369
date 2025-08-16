# ankur_scraper/core/html_extractor.py

from bs4 import BeautifulSoup
import re


def clean_text(text):
    """Normalize and clean extracted text."""
    return re.sub(r"\s+", " ", text).strip()


def get_visible_text_blocks(soup):
    """Yield (title, content) pairs from meaningful sections."""
    sections = []

    # Look into semantic containers first
    for tag in soup.find_all(["main", "section", "article"]):
        heading = tag.find(["h1", "h2", "h3"])
        title = heading.get_text() if heading else "Untitled Section"
        content = clean_text(tag.get_text())
        if content and len(content.split()) > 5:
            sections.append((title, content))

    # Fallback: if no semantic tags found, use top-level headings and paragraphs
    if not sections:
        headings = soup.find_all(["h1", "h2", "h3"])
        for heading in headings:
            title = heading.get_text()
            content = ""
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h1", "h2", "h3"]:
                    break
                if sibling.name in ["p", "div"]:
                    content += " " + sibling.get_text()
            content = clean_text(content)
            if content and len(content.split()) > 5:
                sections.append((title, content))

    return sections


def extract_text_sections(html):
    """Main function to extract sectioned text from HTML."""
    soup = BeautifulSoup(html, "lxml")

    # Remove non-visible elements
    for tag in soup(["script", "style", "noscript", "footer", "nav"]):
        tag.decompose()

    # Skip hidden elements
    for tag in soup.find_all(style=True):
        if "display:none" in tag["style"] or "visibility:hidden" in tag["style"]:
            tag.decompose()

    return get_visible_text_blocks(soup)
