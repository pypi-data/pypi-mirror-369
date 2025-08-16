# ankur_scraper/core/dispatcher.py

import json
import time
from ankur_scraper.core.crawler import get_internal_links
from ankur_scraper.core.page_scraper import scrape_page
from logging_config import get_logger

info_logger = get_logger("info")
error_logger = get_logger("error")
general_logger = get_logger("general")


def run_scraper(url, depth, use_dynamic=False, timeout=10, user_agent=None):
    info_logger.info(f"[bold cyan]🌐 Starting crawl for:[/] {url} (depth={depth})")

    try:
        internal_links = get_internal_links(url, depth, user_agent=user_agent)
    except Exception as e:
        error_logger.error(f"[bold red]❌ Failed during crawling:[/] {e}")
        return

    info_logger.info(f"[bold green]🔗 Found {len(internal_links)} internal links[/]")

    results = []
    success_count = 0
    fail_count = 0
    total_sections = 0

    for link in internal_links:
        start_time = time.time()
        general_logger.info(f"[dim]Scraping:[/] {link}")

        try:
            scraped_sections = scrape_page(link, use_dynamic=use_dynamic, timeout=timeout)
            for section_name, content in scraped_sections:
                results.append({
                    "content": content,
                    "metadata": {
                        "section": section_name,
                        "source_url": link,
                        "extraction_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                })
            duration = round(time.time() - start_time, 2)
            info_logger.info(f"✅ [green]Success[/] - {len(scraped_sections)} sections in {duration}s")
            success_count += 1
            total_sections += len(scraped_sections)
        except Exception as e:
            error_logger.error(f"❌ [red]Failed[/] - {str(e)[:80]}")
            fail_count += 1

    info_logger.info("\n[bold yellow]📊 Summary:[/]")
    info_logger.info(f"  ✅ [green]Successful pages:[/] {success_count}")
    info_logger.info(f"  ❌ [red]Failed pages:[/]     {fail_count}")
    info_logger.info(f"  📄 Total sections:           {total_sections}")

    try:
        return {
            "data": results,
            "summary": {
                "successful_pages": success_count,
                "failed_pages": fail_count,
                "total_sections": total_sections
            }
        }
    except Exception as e:
        error_logger.error(f"[red]❌ Failed to write output file:[/] {e}")