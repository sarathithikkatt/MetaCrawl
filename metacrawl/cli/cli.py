import sys
import argparse
import asyncio
import json
import logging

# On Windows, Playwright requires ProactorEventLoop to work correctly with asyncio.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from metacrawl.utils.helpers import get_configured_pipeline
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

async def main_async(urls, json_output, max_topics, debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
            
    logger.debug(f"CLI args: urls={urls}, json={json_output}, max_topics={max_topics}, debug={debug}")
    
    # Deduplicate URLs while preserving order
    original_count = len(urls)
    seen = set()
    urls = [x for x in urls if not (x in seen or seen.add(x))]
    if len(urls) < original_count:
        logger.info(f"Deduplicated URLs: {original_count} -> {len(urls)}")

    pipeline = get_configured_pipeline()
    results = []
    
    logger.info(f"Starting CLI crawl for {len(urls)} URL(s)")
    for url in urls:
        logger.info(f"Crawling: {url}")
        try:
            data = await pipeline.process_url(url)
            dump = data.model_dump()
            
            if data.error:
                logger.warning(f"Crawl returned error for {url}: {data.error}")
            elif not data.content:
                logger.warning(f"Crawl returned empty content for {url}")
            else:
                logger.debug(f"Crawl OK for {url}: type={data.page_type}, content_len={len(data.content or '')}")
            
            if json_output:
                results.append(dump)
            else:
                if data.error:
                    print(f"\033[91mError crawling {url}: {data.error}\033[0m", file=sys.stderr)
                    if data.status_code:
                        print(f"Status Code: {data.status_code}", file=sys.stderr)
                    print("-" * 40, file=sys.stderr)
                    continue

                print(f"Domain: {dump['domain']}")
                print(f"Page Type: {dump['page_type']}")
                print(f"Title: {dump['title']}")
                print(f"Topics: {', '.join(dump['topics'][:max_topics])}")
                print(f"Content Length: {len(dump['content'])}")
                print(f"Headings Found: {len(dump['headings'])}")
                print("-" * 40)
        except Exception as e:
            logger.error(f"Failed processing {url} from CLI: {e}", exc_info=debug)
            if json_output:
                results.append({
                    "url": url,
                    "error": str(e),
                    "status_code": 500
                })
            else:
                print(f"\033[91mUnexpected error crawling {url}: {e}\033[0m", file=sys.stderr)
                print("-" * 40, file=sys.stderr)
            
    logger.info(f"CLI crawl complete — processed {len(urls)} URL(s)")
    if json_output:
        print(json.dumps(results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="MetaCrawl CLI")
    parser.add_argument("urls", nargs="+", help="URLs to crawl")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--max-topics", type=int, default=5, help="Max topics to print in non-json mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    asyncio.run(main_async(args.urls, args.json, args.max_topics, args.debug))

if __name__ == "__main__":
    main()
