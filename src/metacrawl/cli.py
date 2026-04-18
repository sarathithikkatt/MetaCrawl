import argparse
import asyncio
import json
from .pipeline import CrawlerPipeline

async def main_async(urls, json_output, max_topics):
    pipeline = CrawlerPipeline()
    results = []
    
    # Process sequentially for demonstration.
    for url in urls:
        if not json_output:
            print(f"Crawling {url}...")
        try:
            data = await pipeline.process_url(url)
            dump = data.model_dump()
            
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
            if not json_output:
                print(f"Failed processing {url}: {e}")
            
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
