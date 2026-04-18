import argparse
import asyncio
import json
from metacrawl.utils.helpers import get_configured_pipeline
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

async def main_async(urls, json_output, max_topics):
    logger.debug(f"CLI args: urls={urls}, json={json_output}, max_topics={max_topics}")
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
                print(f"Domain: {dump['domain']}")
                print(f"Page Type: {dump['page_type']}")
                print(f"Title: {dump['title']}")
                print(f"Topics: {', '.join(dump['topics'][:max_topics])}")
                print(f"Content Length: {len(dump['content'])}")
                print(f"Headings Found: {len(dump['headings'])}")
                print("-" * 40)
        except Exception as e:
            logger.error(f"Failed processing {url} from CLI: {e}", exc_info=True)
            
    logger.info(f"CLI crawl complete — processed {len(urls)} URL(s)")
    if json_output:
        print(json.dumps(results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="MetaCrawl CLI")
    parser.add_argument("urls", nargs="+", help="URLs to crawl")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--max-topics", type=int, default=5, help="Max topics to print in non-json mode")
    args = parser.parse_args()
    
    asyncio.run(main_async(args.urls, args.json, args.max_topics))

if __name__ == "__main__":
    main()
