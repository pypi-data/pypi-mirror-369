# tests/test_integration.py

import os
import json
import time
import pytest
from ankur_scraper.dispatcher import run_scraper


@pytest.mark.integration
def test_end_to_end_static_scrape(tmp_path):
    """
    Full scrape of https://example.com with depth=0.
    Verifies output structure and content.
    """
    test_url = "https://example.com"
    output_file = tmp_path / "output.json"

    run_scraper(
        url=test_url,
        depth=0,
        output_path=str(output_file),
        use_dynamic=False,
        timeout=10,
        user_agent="AnkurScraperTestBot/1.0"
    )

    assert output_file.exists(), "Output file was not created."

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert all("content" in item and "metadata" in item for item in data)
    assert all("source_url" in item["metadata"] for item in data)
    assert all("section" in item["metadata"] for item in data)
    assert all("extraction_time" in item["metadata"] for item in data)
    assert any("Example Domain" in item["content"] for item in data)  # Known content


@pytest.mark.integration
def test_end_to_end_dynamic_scrape(tmp_path):
    url = "https://www.pinecone.io/"
    output_path = tmp_path / "output.json"

    run_scraper(
        url=str(url),
        depth=0,
        output_path=str(output_path),
        use_dynamic=True,
        timeout=15,
        user_agent="TestBot"
    )

    assert output_path.exists()
    data = json.load(open(output_path, encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) > 0, "No data returned from scraper."

    valid_content = [item for item in data if len(item["content"].strip()) > 50]
    assert len(valid_content) > 0, "No substantial content extracted (check dynamic mode or selectors)."
