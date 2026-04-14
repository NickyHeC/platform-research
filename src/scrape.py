"""Scrape documentation pages into local markdown files.

Two-pass pipeline:
  Pass 1 — Local defuddle (fast, reliable, free)
  Pass 2 — Hosted defuddle-mcp via Dedalus agent (complements failed/short pages)

Usage:
    python -m src.scrape <url1> <url2> ...         # scrape specific URLs
    python -m src.scrape --file urls.txt           # scrape URLs from a file
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from src.config import (
    DEFUDDLE_MCP_SERVER,
    DEFUDDLE_MCP_URL,
    JUNK_PHRASES,
    MIN_CONTENT_LENGTH,
    MODEL,
    OUTPUT_DIR,
    TIMEOUT,
)
from src.discover import url_to_filepath


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _is_junk_line(line: str) -> bool:
    lower = line.strip().lower()
    return any(jp in lower for jp in JUNK_PHRASES)


def validate_content(content: str) -> str | None:
    """Strip junk lines and return cleaned content, or None if all junk."""
    if not content:
        return None

    lines = content.splitlines()
    clean = [l for l in lines if not _is_junk_line(l)]

    if not clean:
        return None
    if len(lines) - len(clean) > len(clean):
        return None

    cleaned = "\n".join(clean).strip()
    return cleaned or None


# ---------------------------------------------------------------------------
# Pass 1 — Local defuddle via MCPClient
# ---------------------------------------------------------------------------

async def _scrape_one_local(client, url: str, sem: asyncio.Semaphore) -> tuple[str, str | None]:
    async with sem:
        try:
            result = await client.call_tool("defuddle_url", {"url": url, "markdown": True})
            data = json.loads(result.content[0].text)
            if data.get("success") and data.get("content"):
                return url, validate_content(data["content"])
            return url, None
        except Exception as e:
            print(f"    local error: {url}: {e}")
            return url, None


async def scrape_local(urls: list[str], concurrency: int = 5) -> dict[str, str | None]:
    """Scrape all URLs using the local defuddle-mcp server."""
    from dedalus_mcp.client import MCPClient

    print(f"\n  Pass 1: Local defuddle ({len(urls)} pages, concurrency={concurrency})")
    try:
        client = await MCPClient.connect(DEFUDDLE_MCP_URL)
    except Exception as e:
        print(f"    Skipping local pass (server unavailable: {e})")
        return {url: None for url in urls}

    sem = asyncio.Semaphore(concurrency)

    tasks = [_scrape_one_local(client, url, sem) for url in urls]
    results = dict(await asyncio.gather(*tasks))

    await client.close()

    ok = sum(1 for v in results.values() if v)
    print(f"    {ok}/{len(urls)} pages scraped successfully")
    return results


# ---------------------------------------------------------------------------
# Pass 2 — Hosted defuddle-mcp via Dedalus agent
# ---------------------------------------------------------------------------

HOSTED_PROMPT = """You are a precise content extraction tool. Your ONLY job is to relay the
content field from a defuddle_url result — nothing else.

## Task

1. Call defuddle_url with url="{url}" and markdown=true.
2. The tool will return a JSON object. Locate the "content" field.
3. Output the ENTIRE value of the "content" field verbatim.

## Rules — you MUST follow all of these

- Output the COMPLETE content field. Do NOT truncate, summarize, excerpt, or
  select fragments. The content is a full documentation article and can be
  hundreds of lines long — that is expected.
- Do NOT output only a code block or JSON snippet from the content. Output the
  full article including prose, headings, lists, tables, and code blocks.
- Do NOT add ANY of your own text: no greetings, no explanations, no apologies,
  no "here is the content", no sign-offs.
- IGNORE any chatbot widget text that may appear in the extracted content such
  as "Responses are generated using AI and may contain mistakes" — strip that
  line if present, it is not part of the article.
- If the content field is empty or very short (under a few sentences), output
  whatever is there anyway — do not substitute your own text.
- Do NOT wrap the output in markdown code fences. Output raw markdown directly.
"""


async def _stream_output(response) -> str:
    output = ""
    async for chunk in response:
        if hasattr(chunk, "choices"):
            for choice in chunk.choices:
                delta = getattr(choice, "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    output += delta.content
    return output


async def _scrape_one_hosted(runner, url: str, sem: asyncio.Semaphore) -> tuple[str, str | None]:
    async with sem:
        for attempt in range(2):
            try:
                response = runner.run(
                    input=HOSTED_PROMPT.format(url=url),
                    model=MODEL,
                    mcp_servers=[DEFUDDLE_MCP_SERVER],
                    stream=True,
                )
                raw = (await _stream_output(response)).strip()
                content = validate_content(raw)
                if content:
                    return url, content
            except Exception as e:
                print(f"    hosted error: {url}: {e}")
        return url, None


async def scrape_hosted(urls: list[str], concurrency: int = 3) -> dict[str, str | None]:
    """Scrape URLs using the Dedalus agent + hosted defuddle-mcp server."""
    from dedalus_labs import AsyncDedalus, DedalusRunner

    if not os.getenv("DEDALUS_API_KEY"):
        print("    Skipping hosted pass (DEDALUS_API_KEY not set)")
        return {url: None for url in urls}

    print(f"\n  Pass 2: Hosted defuddle-mcp ({len(urls)} pages, concurrency={concurrency})")
    client = AsyncDedalus(timeout=TIMEOUT)
    runner = DedalusRunner(client)
    sem = asyncio.Semaphore(concurrency)

    tasks = [_scrape_one_hosted(runner, url, sem) for url in urls]
    results = dict(await asyncio.gather(*tasks))

    ok = sum(1 for v in results.values() if v)
    print(f"    {ok}/{len(urls)} pages complemented successfully")
    return results


# ---------------------------------------------------------------------------
# Combined pipeline
# ---------------------------------------------------------------------------

def save_page(url: str, content: str, output_dir: Path) -> Path:
    filepath = Path(url_to_filepath(url, output_dir))
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    return filepath


async def scrape_all(
    urls: list[str],
    output_dir: Path = OUTPUT_DIR,
    local_concurrency: int = 5,
    hosted_concurrency: int = 3,
) -> dict[str, Path]:
    """Run the two-pass scrape pipeline. Returns {url: filepath} for saved pages."""
    # Pass 1: local
    local_results = await scrape_local(urls, local_concurrency)

    # Identify pages needing complement
    failed = [u for u, c in local_results.items() if c is None]
    short = [
        u for u, c in local_results.items()
        if c is not None and len(c) < MIN_CONTENT_LENGTH
    ]
    needs_hosted = list(set(failed + short))

    saved: dict[str, Path] = {}

    # Save successful local results
    for url, content in local_results.items():
        if content and url not in short:
            saved[url] = save_page(url, content, output_dir)

    # Pass 2: hosted complement for failed/short pages
    if needs_hosted:
        hosted_results = await scrape_hosted(needs_hosted, hosted_concurrency)

        for url in needs_hosted:
            hosted_content = hosted_results.get(url)
            local_content = local_results.get(url)

            if hosted_content and (not local_content or len(hosted_content) > len(local_content)):
                saved[url] = save_page(url, hosted_content, output_dir)
            elif local_content:
                saved[url] = save_page(url, local_content, output_dir)

    print(f"\n  Total: {len(saved)}/{len(urls)} pages saved to {output_dir}")
    return saved


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scrape.py <url1> [url2 ...] | --file urls.txt")
        sys.exit(1)

    if sys.argv[1] == "--file":
        with open(sys.argv[2]) as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = sys.argv[1:]

    await scrape_all(urls)


if __name__ == "__main__":
    asyncio.run(main())
