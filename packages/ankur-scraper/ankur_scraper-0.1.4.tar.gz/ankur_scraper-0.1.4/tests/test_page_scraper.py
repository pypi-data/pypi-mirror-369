from core.page_scraper import scrape_page

def test_scrape_page_static():
    url = "https://www.pinecone.io/"
    sections = scrape_page(url, use_dynamic=False)
    assert isinstance(sections, list)

def test_scrape_page_dynamic():
    url = "https://www.pinecone.io/"
    sections = scrape_page(url, use_dynamic=True)
    assert isinstance(sections, list)
    assert any(len(s[1]) > 50 for s in sections)
