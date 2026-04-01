"""Shared configuration for the provider-research pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFUDDLE_MCP_URL = os.getenv("DEFUDDLE_MCP_URL", "http://127.0.0.1:8080/mcp")
DEFUDDLE_MCP_SERVER = os.getenv("DEFUDDLE_MCP_SERVER", "nickyhec/defuddle-mcp")
MODEL = os.getenv("MODEL", "anthropic/claude-sonnet-4-20250514")
TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "600"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "docs"))

JUNK_PHRASES = [
    "responses are generated using ai",
    "may contain mistakes",
    "i apologize",
    "i'm sorry",
    "i cannot",
    "i'm unable",
    "unfortunately",
    "as an ai",
    "i don't have access",
    "the content field appears",
    "the content field contains only",
    "the content field is empty",
    "was not successfully extracted",
    "not been properly extracted",
    "the actual documentation content",
    "as instructed",
    "built with mintlify",
    "built with [mintlify",
]

MIN_CONTENT_LENGTH = 200
