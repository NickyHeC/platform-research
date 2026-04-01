"""Provider Research — scrape a provider's API docs and generate a PROJECT.md.

Given a starting URL to a provider's API documentation, this tool:
  1. Discovers all documentation pages (via llms.txt or link extraction)
  2. Scrapes them using local defuddle (fast) + hosted defuddle-mcp (complement)
  3. Generates a filled-in PROJECT.md from the scraped content

Usage:
    python -m src.research https://developers.example.com/docs

    python -m src.research https://developers.example.com/docs \\
        --prefix /docs \\
        --output-dir my-docs \\
        --concurrency 5
"""

import asyncio
import sys
from pathlib import Path

from src.config import OUTPUT_DIR
from src.discover import discover_pages
from src.generate_project import generate_project_md
from src.scrape import scrape_all


async def run(
    start_url: str,
    docs_prefix: str | None = None,
    output_dir: Path = OUTPUT_DIR,
    local_concurrency: int = 5,
    hosted_concurrency: int = 3,
) -> None:
    print("Provider Research")
    print("=" * 60)
    print(f"  Start URL:  {start_url}")
    print(f"  Output dir: {output_dir.resolve()}")
    print("=" * 60)

    # Step 1: Discover
    print("\nStep 1: Discovery")
    print("-" * 40)
    urls = await discover_pages(start_url, docs_prefix)

    if not urls:
        print("  No pages found. Check the URL and try again.")
        return

    print(f"  {len(urls)} pages to scrape")

    # Step 2: Scrape
    print("\nStep 2: Scraping")
    print("-" * 40)
    saved = await scrape_all(
        urls,
        output_dir=output_dir,
        local_concurrency=local_concurrency,
        hosted_concurrency=hosted_concurrency,
    )

    if not saved:
        print("\n  No pages were saved. Cannot generate PROJECT.md.")
        return

    # Step 3: Generate PROJECT.md
    print()
    print("-" * 40)
    project_path = await generate_project_md(docs_dir=output_dir)

    # Summary
    print()
    print("=" * 60)
    print("Done!")
    print(f"  Docs:       {len(saved)} pages in {output_dir.resolve()}")
    print(f"  PROJECT.md: {project_path.resolve()}")
    print("=" * 60)


async def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)

    start_url = sys.argv[1]
    docs_prefix = None
    output_dir = OUTPUT_DIR
    local_concurrency = 5
    hosted_concurrency = 3

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--prefix" and i + 1 < len(args):
            docs_prefix = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = Path(args[i + 1])
            i += 2
        elif args[i] == "--concurrency" and i + 1 < len(args):
            local_concurrency = int(args[i + 1])
            i += 2
        elif args[i] == "--hosted-concurrency" and i + 1 < len(args):
            hosted_concurrency = int(args[i + 1])
            i += 2
        else:
            i += 1

    await run(
        start_url=start_url,
        docs_prefix=docs_prefix,
        output_dir=output_dir,
        local_concurrency=local_concurrency,
        hosted_concurrency=hosted_concurrency,
    )


if __name__ == "__main__":
    asyncio.run(main())
