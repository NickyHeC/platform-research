# Provider Research

Researches a provider's API documentation and generates a filled-in `PROJECT.md` ready for building an MCP server.

Given a starting URL, the tool automatically:
1. **Discovers** all documentation pages (via `llms.txt` or link extraction)
2. **Scrapes** them using local [defuddle](https://github.com/kepano/defuddle) (fast, free) with a [hosted defuddle-mcp](https://dedalus.dev/mcp/nickyhec/defuddle-mcp) complement pass for failed pages
3. **Generates** a `PROJECT.md` using a Dedalus agent that reads all the scraped docs and fills in the [mcp-template](https://github.com/NickyHeC/mcp-template) format

## Prerequisites

- Python >= 3.10
- Node.js >= 18 (for defuddle CLI)
- A running [defuddle-mcp](https://github.com/nickyhec/defuddle-mcp) server locally
- A [Dedalus API key](https://dedalus.dev/dashboard/api-keys)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env and add your DEDALUS_API_KEY
```

## Usage

```bash
# Start the local defuddle-mcp server (separate terminal)
cd /path/to/defuddle-mcp && uv run python -m src.main

# Run the full pipeline
python -m src.research https://developers.example.com/docs

# With options
python -m src.research https://developers.example.com/docs \
    --prefix /docs \
    --output-dir my-docs \
    --concurrency 5
```

## Pipeline

| Step | Module | What it does |
|------|--------|-------------|
| 1 | `src/discover.py` | Finds all doc pages via `llms.txt` or link extraction |
| 2 | `src/scrape.py` | Two-pass scrape: local defuddle first, hosted MCP complement |
| 3 | `src/generate_project.py` | Dedalus agent reads all docs and fills in `PROJECT.md` |
| — | `src/research.py` | Orchestrates all three steps |

## Output

```
docs/                    # Scraped markdown files mirroring the docs site structure
PROJECT.md               # Filled-in project research document
```

The `PROJECT.md` follows the [mcp-template](https://github.com/NickyHeC/mcp-template) format and includes platform overview, authentication details, endpoint inventory, rate limits, and response format notes — everything needed to build an MCP server.
