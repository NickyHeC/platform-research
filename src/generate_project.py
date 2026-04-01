"""Generate a filled PROJECT.md from scraped documentation.

Reads all scraped markdown files, sends them to the Dedalus agent along with
the PROJECT.md template, and writes the filled-in result.

Usage:
    python -m src.generate_project                       # reads from docs/
    python -m src.generate_project --docs-dir my-docs/   # custom docs dir
"""

import asyncio
import os
import sys
from pathlib import Path

from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

from src.config import MODEL, OUTPUT_DIR, TIMEOUT

load_dotenv()

PROJECT_TEMPLATE = Path(__file__).parent.parent / "PROJECT_TEMPLATE.md"
MAX_DOCS_CHARS = 150_000


def _load_template() -> str:
    if PROJECT_TEMPLATE.exists():
        return PROJECT_TEMPLATE.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Template not found: {PROJECT_TEMPLATE}")


def _load_docs(docs_dir: Path) -> str:
    """Concatenate all scraped markdown files with source headers."""
    md_files = sorted(docs_dir.rglob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {docs_dir}")

    parts: list[str] = []
    total = 0

    for f in md_files:
        content = f.read_text(encoding="utf-8").strip()
        if not content:
            continue
        rel = f.relative_to(docs_dir)
        header = f"<!-- SOURCE: {rel} -->"
        chunk = f"{header}\n{content}\n"

        if total + len(chunk) > MAX_DOCS_CHARS:
            parts.append(f"\n<!-- TRUNCATED: {len(md_files) - len(parts)} files omitted (context limit) -->\n")
            break

        parts.append(chunk)
        total += len(chunk)

    print(f"  Loaded {len(parts)} doc files ({total:,} chars)")
    return "\n---\n\n".join(parts)


def _build_prompt(template: str, docs: str) -> str:
    return f"""You are an expert technical writer filling in a project research document.

## Your task

Below you will find:
1. A PROJECT.md TEMPLATE with empty fields to fill in
2. SCRAPED DOCUMENTATION from the target platform's API docs

Read through ALL the scraped documentation carefully. Then fill in EVERY section
of the PROJECT.md template based on what you learned from the docs.

## Rules

- Fill in every field. If the docs don't contain information for a field, write
  "Not found in docs — needs manual research" rather than leaving it blank.
- For the "Endpoints / Features to Implement" table, list the MOST IMPORTANT
  and commonly used API endpoints. Aim for 8-15 tools. Focus on CRUD operations,
  search/query, and the platform's core features.
- For authentication, be very specific — note the exact header format, token
  names, and how credentials are obtained.
- Include actual example curl commands or code snippets for the "Example
  authenticated request" section if the docs show them.
- For "Response Format Notes", include a real example JSON response if available.
- Output ONLY the filled-in PROJECT.md content. No commentary or explanations
  outside the document.
- Keep the same markdown structure and section headers as the template.

## PROJECT.md TEMPLATE

{template}

## SCRAPED DOCUMENTATION

{docs}
"""


async def generate_project_md(
    docs_dir: Path = OUTPUT_DIR,
    output_path: Path | None = None,
) -> Path:
    """Read scraped docs and generate a filled PROJECT.md."""
    if output_path is None:
        output_path = Path("PROJECT.md")

    if not os.getenv("DEDALUS_API_KEY"):
        print("\nError: DEDALUS_API_KEY not set. See env.example.")
        sys.exit(1)

    print("\nStep 3: Generating PROJECT.md")
    print("=" * 50)

    template = _load_template()
    docs = _load_docs(docs_dir)
    prompt = _build_prompt(template, docs)

    print(f"  Prompt size: {len(prompt):,} chars")
    print(f"  Sending to agent ({MODEL})…")

    client = AsyncDedalus(timeout=TIMEOUT)
    runner = DedalusRunner(client)

    response = runner.run(
        input=prompt,
        model=MODEL,
        stream=True,
    )

    output = ""
    async for chunk in response:
        if hasattr(chunk, "choices"):
            for choice in chunk.choices:
                delta = getattr(choice, "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    output += delta.content

    output = output.strip()

    if not output:
        print("  Error: agent returned empty output")
        sys.exit(1)

    output_path.write_text(output, encoding="utf-8")
    print(f"  Written to {output_path} ({len(output):,} chars)")
    return output_path


async def main() -> None:
    docs_dir = OUTPUT_DIR
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--docs-dir" and i < len(sys.argv) - 1:
            docs_dir = Path(sys.argv[i + 1])

    await generate_project_md(docs_dir)


if __name__ == "__main__":
    asyncio.run(main())
