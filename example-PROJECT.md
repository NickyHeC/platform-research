# PROJECT.md — Platform Research Notes

> This file is a working notepad for the developer (or AI coding agent) building
> this MCP server. Fill in each section as you research the target platform.
> The information here drives the implementation in `src/main.py` and `src/tools.py`.
>
> **Do not commit secrets.** Store credentials in `.env` (which is gitignored).

---

## Platform Overview

**Platform name:** Notion API
**Official docs:** https://developers.notion.com/reference/intro
**Base URL:** `https://api.notion.com/v1`

Brief description of what this platform does and why we are building an MCP server for it:

Notion is an all-in-one workspace that combines notes, tasks, wikis, and databases. The Notion API allows developers to interact with Notion workspaces programmatically, enabling automation of content creation, data synchronization, and workflow management. Building an MCP server for Notion allows AI agents to read, write, and manipulate Notion content, making it easier to integrate Notion into AI-powered workflows for documentation, project management, and knowledge management.

---

## Authentication

**Auth type:** Bearer Token (Internal Integration)
**How to obtain credentials:** https://www.notion.so/my-integrations (create an internal integration)

### Credential details

- **Token / key name:** `NOTION_API_KEY`
- **Header format:** `Authorization: Bearer {api_key}`
- **Scopes required:** (configured in integration settings)
  - Read content
  - Read user information without email
  - Insert content
  - Update content and properties
  - Read comments
  - Insert comments

### OAuth-specific (skip if using API Key)

Not applicable - using Internal Integration with Bearer Token

### Example authenticated request

```bash
curl 'https://api.notion.com/v1/users/me' \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H 'Notion-Version: 2026-03-11'
```

---

## Endpoints / Features to Implement

List the API endpoints or features you plan to expose as MCP tools.
For each, note the HTTP method, path, key parameters, and response shape.

| Tool name | Method | Path | Description |
|-----------|--------|------|-------------|
| search_notion | POST | `/v1/search` | Search across all pages and databases in workspace |
| get_page | GET | `/v1/pages/{page_id}` | Retrieve a specific page with properties |
| create_page | POST | `/v1/pages` | Create a new page in workspace or database |
| update_page | PATCH | `/v1/pages/{page_id}` | Update page properties and content |
| get_page_content | GET | `/v1/blocks/{block_id}/children` | Get child blocks (content) of a page |
| append_page_content | PATCH | `/v1/blocks/{block_id}/children` | Add blocks to existing page content |
| get_database | GET | `/v1/databases/{database_id}` | Retrieve database schema and properties |
| query_database | POST | `/v1/databases/{database_id}/query` | Query database with filters and sorting |
| create_database | POST | `/v1/databases` | Create a new database |
| get_page_markdown | GET | `/v1/pages/{page_id}/markdown` | Retrieve page content as markdown |
| update_page_markdown | PATCH | `/v1/pages/{page_id}/markdown` | Update page content using markdown |
| get_comments | GET | `/v1/comments` | List comments on a page or block |
| add_comment | POST | `/v1/comments` | Add comment to page or discussion thread |
| list_users | GET | `/v1/users` | List all users in workspace |
| upload_file | POST | `/v1/file_uploads` | Upload files to attach to pages/blocks |

---

## Rate Limits and Restrictions

- **Rate limit:** 3 requests per second per integration
- **Retry strategy:** Exponential backoff, respect `Retry-After` header when rate limited
- **Other restrictions:** 
  - Must use `Notion-Version` header (recommended: `2026-03-11`)
  - File uploads limited to 5 MiB (free) / 5 GiB (paid workspaces)
  - Maximum 100 results per paginated response
  - Integration must be explicitly connected to pages/databases to access them
  - Some block types are read-only (e.g., AI meeting notes)

---

## Response Format Notes

Describe the general shape of API responses — JSON structure, pagination style,
error format, etc. Paste a representative example if helpful.

```json
{
  "object": "list",
  "results": [
    {
      "object": "page",
      "id": "b55c9c91-384d-452b-81db-d1ef79372b75",
      "created_time": "2020-03-17T19:10:04.968Z",
      "last_edited_time": "2020-03-17T21:49:37.913Z",
      "parent": {
        "type": "database_id",
        "database_id": "d9824bdc-8445-4327-be8b-5b47500af6ce"
      },
      "properties": {
        "Name": {
          "type": "title",
          "title": [
            {
              "type": "text",
              "text": {"content": "Example Page"}
            }
          ]
        }
      }
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

Common patterns:
- Paginated responses use `has_more` and `next_cursor` for pagination
- All objects have `object` and `id` fields
- Type-specific data follows pattern: object has `type` field and matching property (e.g., `"type": "paragraph"` has `"paragraph": {}`)
- Rich text is arrays of rich text objects with formatting and content
- Errors follow standard HTTP status codes with detailed error objects

---

## Token / Credential Notes

Notes on token lifecycle, expiry, rotation, or platform-specific quirks:

- Internal integration tokens do not expire automatically
- Tokens can be regenerated manually in the integration settings
- Integration must be explicitly connected to pages/databases by workspace members
- Bot users appear in workspace with integration name and icon
- Integration permissions are set at creation time and control capabilities
- API version is controlled by `Notion-Version` header, not token

---

## Additional References

- API Reference: https://developers.notion.com/reference/intro
- Getting Started Guide: https://developers.notion.com/docs/getting-started
- Working with Databases: https://developers.notion.com/docs/working-with-databases
- Working with Page Content: https://developers.notion.com/docs/working-with-page-content
- Enhanced Markdown Format: https://developers.notion.com/guides/data-apis/enhanced-markdown
- JavaScript SDK: https://github.com/makenotion/notion-sdk-js
- Community Examples: https://github.com/makenotion/notion-sdk-js/tree/main/examples

---

## Notes for README

Bullet points to include in the project README when it is written:

- Provides comprehensive access to Notion workspaces through MCP protocol
- Supports both block-based and markdown-based content manipulation
- Includes database operations (create, query, update) and page management
- Handles file uploads and media attachments
- Supports commenting system for collaborative workflows
- Requires internal integration setup and explicit page/database connections
- Rate limited to 3 requests per second - includes automatic retry logic
- Supports advanced features like database templates and AI meeting notes
- Compatible with Claude, Cursor, and other MCP-enabled AI tools