# ankur_scraper/cli.py

import argparse
from ankur_scraper.dispatcher import run_scraper


def main():
    parser = argparse.ArgumentParser(
        description="Ankur Scraper - Crawl and extract text content from websites."
    )

    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The base URL of the website to scrape (e.g., https://example.com)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Depth of link crawling within the domain (default: 1)",
    )
    parser.add_argument(
        "--dynamic",
        action="store_true",
        help="Enable dynamic scraping using headless browser for JS-rendered content",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default=None,
        help="Custom User-Agent string (optional)",
    )

    args = parser.parse_args()

    run_scraper(
        url=args.url,
        depth=args.depth,
        use_dynamic=args.dynamic,
        timeout=args.timeout,
        user_agent=args.user_agent,
    )


if __name__ == "__main__":
    main()
