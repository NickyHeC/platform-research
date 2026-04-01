The open-source `notion-mcp-server` package is no longer actively maintained. We recommend using the remote [Notion MCP](https://developers.notion.com/guides/mcp/get-started-with-mcp) server for the best experience. Issues and pull requests on the open-source repository are not actively monitored.

If you need to run your own MCP server, the [`notion-mcp-server` package](https://github.com/makenotion/notion-mcp-server) is available as an open-source implementation. This option may be suitable if you:
- Need bearer token authentication for fully automated workflows
- Already have an existing Notion integration you want to reuse
- Require access to the original JSON-based v1 APIs
- Prefer to manage infrastructure yourself
Compared to Notion’s remote MCP, running the open-source server requires more technical setup, including provisioning your own Notion integration, managing API tokens, and handling deployment.

For most use cases, we recommend connecting to the remote Notion MCP server at `https://mcp.notion.com/mcp`. It requires no infrastructure setup, stays up-to-date automatically, and includes tools optimized specifically for AI agents.

**What’s Next** If you still want to self-host, explore the [GitHub repo](https://github.com/makenotion/notion-mcp-server) to get started. For the recommended approach, see [Connecting to Notion MCP](https://developers.notion.com/guides/mcp/get-started-with-mcp).