"""Discover all documentation pages from a starting URL.

Tries multiple strategies in order:
  1. llms.txt at the domain root (common on Mintlify-powered docs)
  2. Link extraction from the starting page via defuddle

Usage:
    python -m src.discover https://developers.example.com/docs
    python -m src.discover https://developers.example.com/docs --prefix /docs
"""

import asyncio
import json
import re
import sys
from urllib.parse import urlparse

import httpx

from src.config import DEFUDDLE_MCP_URL


async def discover_from_llms_txt(base_url: str) -> list[str] | None:
    """Fetch llms.txt from the domain root and parse URLs from it."""
    parsed = urlparse(base_url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"

    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        try:
            resp = await client.get(llms_url)
            if resp.status_code != 200:
                return None

            urls: list[str] = []
            for line in resp.text.splitlines():
                match = re.search(r"\[.*?\]\((https?://[^\)]+)\)", line)
                if match:
                    url = match.group(1)
                    if url.endswith(".md"):
                        url = url[:-3]
                    urls.append(url)

            return urls if urls else None
        except Exception:
            return None


async def discover_from_page(
    start_url: str,
    docs_prefix: str,
) -> list[str]:
    """Extract links from a page using local defuddle-mcp."""
    from dedalus_mcp.client import MCPClient

    try:
        client = await MCPClient.connect(DEFUDDLE_MCP_URL)
    except Exception:
        print("    Local defuddle unavailable, returning start URL only")
        return [start_url]

    try:
        result = await client.call_tool("defuddle_url", {
            "url": start_url,
            "markdown": True,
        })
        data = json.loads(result.content[0].text)
        if not data.get("success") or not data.get("content"):
            return [start_url]

        parsed = urlparse(start_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        skip_ext = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".ico", ".css", ".js")

        links: set[str] = set()
        for match in re.finditer(r"\[.*?\]\(([^\)]+)\)", data["content"]):
            href = match.group(1).split("#")[0].rstrip("/")
            if not href:
                continue
            if href.startswith("/"):
                href = base_domain + href
            if (
                href.startswith(base_domain)
                and docs_prefix in href
                and not href.lower().endswith(skip_ext)
            ):
                links.add(href)

        all_urls = sorted(links)
        if start_url not in all_urls:
            all_urls.insert(0, start_url)
        return all_urls
    finally:
        await client.close()


async def discover_pages(
    start_url: str,
    docs_prefix: str | None = None,
) -> list[str]:
    """Discover all documentation pages reachable from a starting URL.

    Returns a sorted, deduplicated list of URLs.
    """
    parsed = urlparse(start_url)

    if docs_prefix is None:
        path_parts = parsed.path.strip("/").split("/")
        docs_prefix = "/" + path_parts[0] if path_parts and path_parts[0] else "/"

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    print(f"  Discovering pages under {base_url}{docs_prefix}…")

    # Strategy 1: llms.txt
    llms_urls = await discover_from_llms_txt(base_url)
    if llms_urls:
        filtered = [u for u in llms_urls if docs_prefix in u]
        if filtered:
            print(f"  Found llms.txt with {len(filtered)} pages (filtered from {len(llms_urls)})")
            return filtered

    # Strategy 2: link extraction from the starting page
    print("  No llms.txt found, extracting links from starting page…")
    page_urls = await discover_from_page(start_url, docs_prefix)
    print(f"  Found {len(page_urls)} pages via link extraction")
    return page_urls


def url_to_filepath(url: str, output_dir) -> str:
    """Convert a URL to a local file path mirroring the URL structure."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    return str(output_dir / f"{path}.md")


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python discover.py <start_url> [--prefix <path_prefix>]")
        sys.exit(1)

    start_url = sys.argv[1]
    prefix = None
    if "--prefix" in sys.argv:
        idx = sys.argv.index("--prefix")
        if idx + 1 < len(sys.argv):
            prefix = sys.argv[idx + 1]

    urls = await discover_pages(start_url, prefix)
    print(f"\nDiscovered {len(urls)} pages:\n")
    for u in urls:
        print(f"  {u}")


if __name__ == "__main__":
    asyncio.run(main())
