# 🕷️ Ankur Scraper

**Ankur Scraper** is a modular, production-ready website scraping tool built with Python. It crawls and extracts structured content from websites — including dynamic pages rendered with JavaScript — and saves the results in a clean JSON format.

---

## 🚀 Features

- ✅ Crawl internal links (with max depth)
- ✅ Extract visible, structured text (section-wise)
- ✅ Supports static and dynamic (JS-rendered) pages
- ✅ Respects `robots.txt`
- ✅ CLI interface with arguments
- ✅ Logs everything to file + rich-colored terminal
- ✅ Testable, extensible, and publishable as a Python package

---

## 📦 Project Structure

```bash
ankur_scraper/
├── ankur_scraper/
│ ├── init.py
│ ├── cli.py
│ ├── core/
│ │ ├── crawler.py
│ │ ├── dispatcher.py
│ │ ├── html_extractor.py
│ │ ├── page_scraper.py
│ ├── logging_config.py
│ └── logs/
│ ├── info.log
│ ├── error.log
│ └── general.log
├── tests/
│ ├── test_crawler.py
│ ├── test_html_extractor.py
│ ├── test_page_scraper.py
│ ├── test_integration.py
│ └── conftest.py
├── requirements.txt
├── setup.py
└── README.md
```

## 🔧 Installation

Clone the project and install dependencies:

```bash
git clone https://github.com/your-org/ankur_scraper.git
cd ankur_scraper
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt

# Install Playwright drivers (for dynamic scraping)
playwright install
```

## 🕹️ Usage (CLI)

```bash
python -m ankur_scraper.cli \
  --url "https://example.com" \
  --depth 1 \
  --output results.json \
  --dynamic \
  --timeout 10
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--url` | Starting URL to scrape (required) |
| `--depth` | How deep to crawl within the domain |
| `--output` | File path to save JSON output |
| `--dynamic` | Use dynamic scraping (Playwright) |
| `--timeout` | Timeout for each page (seconds) |

## Usage Examples

```bash
# Basic usage
script --url https://example.com

# With depth and output
script --url https://example.com --depth 2 --output results.json

# With dynamic scraping and timeout
script --url https://example.com --dynamic --timeout 30
```

## 🧪 Running Tests

### Unit Tests

```bash
pytest tests/ --tb=short
```

### Integration Tests (Live Web)

```bash
pytest tests/test_integration.py -m integration
```

Integration tests make real HTTP calls to sites like example.com.

Add pytest.ini for markers:

```ini
# pytest.ini
[pytest]
markers =
    integration: mark tests as integration
```

## 📄 Output Format

Every page section is saved as a structured object:

```json
{
  "content": "Text content here...",
  "metadata": {
    "section": "About Us",
    "source_url": "https://example.com/about",
    "extraction_time": "2025-07-14 12:34:56"
  }
}
```

## 📚 Logging

Logs are written to both terminal and file:

- logs/info.log: general operations
- logs/error.log: failed links and errors
- logs/general.log: warnings, summaries

Terminal output is rich-colored with emojis and timestamps.

## 📦 Packaging & Publishing

This scraper is fully structured as a pip-installable package.

Install Locally for CLI Use

```bash
pip install .
```

Now you can run:

```bash
ankur-scraper --url "https://..." --output output.json
```

### Publish to PyPI

Ensure you have build and twine:

```bash
pip install build twine
```

### Build and publish

```bash
python -m build
twine upload dist/*
```

Update version in setup.py before publishing!

## 📌 Dependencies

- httpx: Fast, async-capable HTTP requests
- beautifulsoup4 + lxml: HTML parsing
- tldextract: Domain filtering
- playwright: JS rendering (headless)
- rich: Beautiful terminal output
- pytest: Testing

## 🤝 Contributing

- Fork the repo
- Make changes in a branch
- Run tests: pytest
- Submit a PR

## 🧠 Future Ideas

- Save to Markdown or plaintext
- URL exclusion filters
- Config file/ENV mode
- Docker support
- CI/CD for publishing

## 🧑‍💻 Maintainer

Made with ❤️ by Ankur Global Solutions
