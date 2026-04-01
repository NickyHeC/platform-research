## Overview

When a user installs a public integration, the integration often needs to set up structured content in the user’s workspace — for example, a project tracker database with pre-configured views, or a set of pages with a specific layout. Historically, the recommended approach was to configure a [template URL during OAuth](https://developers.notion.com/guides/get-started/authorization#prompt-for-an-integration-with-a-notion-template-option). When a user authorizes the integration, they can choose to duplicate a static Notion page into their workspace. While this works, it has limitations:
- The template is a snapshot — it can’t adapt to the user’s existing workspace or preferences.
- The integration can’t customize the setup based on user choices during onboarding.
- The duplicated content may include boilerplate that doesn’t apply to every user.
A more flexible approach is to build the workspace content **programmatically** using the API. Public integrations can create top-level pages and databases directly in a user’s workspace, configure views, and apply templates — all tailored to what the user actually needs.

## Create workspace-level pages and databases.

## Configure views on new databases.

## Populate pages using templates.

## How it works

The end-to-end flow looks like this:

## Creating workspace-level content

Public integrations can create pages and databases at the **workspace level** by omitting the `parent` parameter (or setting it to `{ "type": "workspace", "workspace": true }`). This places the content in the authorizing user’s Private section.

This capability is only available to **public integrations**. Internal integrations cannot create workspace-level content because they aren’t owned by a single user.

### Create a database

```shellscript
curl -X POST https://api.notion.com/v1/databases \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "title": [{ "type": "text", "text": { "content": "Project Tracker" } }],
    "is_inline": false,
    "initial_data_source": {
      "properties": {
        "Task": { "title": {} },
        "Status": {
          "status": {
            "options": [
              { "name": "Not started", "color": "default" },
              { "name": "In progress", "color": "blue" },
              { "name": "Done", "color": "green" }
            ]
          }
        },
        "Assignee": { "people": {} },
        "Due date": { "date": {} }
      }
    }
  }'
```

The new database is created with one data source and one default Table view. Store the `database.id` and `database.data_sources[0].id` — you’ll need them to create views and pages.

### Create a standalone page

```shellscript
curl -X POST https://api.notion.com/v1/pages \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "properties": {
      "title": {
        "title": [{ "type": "text", "text": { "content": "Getting Started" } }]
      }
    },
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [{ "type": "text", "text": { "content": "Welcome!" } }]
        }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [
            { "type": "text", "text": { "content": "This page was created by your integration. You can move it anywhere in your workspace." } }
          ]
        }
      }
    ]
  }'
```

## Adding views

After creating a database, you can add views that match your integration’s use cases. Each database starts with a default Table view, but you’ll likely want to create additional views with specific filters, sorts, and layout types. For a project tracker, you might want a Board view grouped by status and a Calendar view for due dates:

```shellscript
# Board view: tasks grouped by status
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Task board",
    "type": "board"
  }'

# Calendar view: tasks by due date
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Schedule",
    "type": "calendar"
  }'

# Filtered table: only active tasks
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Active tasks",
    "type": "table",
    "filter": {
      "property": "Status",
      "status": {
        "does_not_equal": "Done"
      }
    },
    "sorts": [
      {
        "property": "Due date",
        "direction": "ascending"
      }
    ]
  }'
```

See the [Working with views](https://developers.notion.com/guides/data-apis/working-with-views) guide for full details on creating, updating, and querying views.

## Applying templates

If your integration pre-configures [database templates](https://www.notion.com/help/database-templates) for the data source, you can create pages that start from those templates. This is useful for providing users with structured starting points — for example, a “Bug report” template with pre-filled sections.

```shellscript
# List available templates for the data source
curl -X GET "https://api.notion.com/v1/data_sources/DATA_SOURCE_ID/templates" \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"

# Create a page using the default template
curl -X POST https://api.notion.com/v1/pages \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "parent": {
      "type": "data_source_id",
      "data_source_id": "DATA_SOURCE_ID"
    },
    "properties": {
      "Task": {
        "title": [{ "type": "text", "text": { "content": "My first task" } }]
      }
    },
    "template": {
      "type": "default"
    }
  }'
```

Template content is applied asynchronously after the page is created. If your integration needs to take action once the template is fully applied, use [webhooks](https://developers.notion.com/reference/webhooks) to listen for `page.content_updated` events. See the [Creating pages from templates](https://developers.notion.com/guides/data-apis/creating-pages-from-templates) guide for the full workflow.

## Comparison with template URL duplication

|  | Template URL (OAuth) | Programmatic setup |
| --- | --- | --- |
| **Customization** | Static — every user gets the same template | Dynamic — tailor content to each user |
| **Schema control** | Template is a snapshot; schema changes require updating the source page | Full control over database schema, properties, and views at creation time |
| **Multiple databases** | One template page per integration | Create as many databases and pages as needed |
| **View configuration** | Views are duplicated as-is from the template | Create views programmatically with specific filters, sorts, and types |
| **User interaction** | User must choose “Duplicate template” during OAuth | No extra user interaction needed — setup happens after authorization |
| **Template URL still useful?** | Yes — it’s simpler for basic use cases where a static template is sufficient | Use programmatic setup when you need flexibility or when the template URL approach doesn’t cover your needs |

The template URL approach still works and is fine for simple integrations. Programmatic setup is recommended when your integration needs to create multiple resources, customize content per user, or keep the workspace structure in sync with external systems over time.

- [Working with views](https://developers.notion.com/guides/data-apis/working-with-views) — full reference for creating, updating, and querying views.
- [Creating pages from templates](https://developers.notion.com/guides/data-apis/creating-pages-from-templates) — detailed guide on using data source templates.
- [Working with databases](https://developers.notion.com/guides/data-apis/working-with-databases) — database schemas, querying, and page management.
- [Authorization](https://developers.notion.com/guides/get-started/authorization) — the OAuth flow for public integrations.