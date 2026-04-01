The Views API requires API version `2025-09-03` or later. If your integration uses an older version, see the [upgrade guide](https://developers.notion.com/guides/get-started/upgrade-guide-2025-09-03) for migration steps.

## Overview

[Database views](https://www.notion.so/help/views-filters-and-sorts) let users see the same data in different ways — for example, as a table, board, calendar, timeline, gallery, list, form, chart, map, or dashboard. Each view can have its own filters, sorts, and layout configuration, so a single database can serve many different workflows. The Notion API exposes views as first-class resources. This means integrations can programmatically manage the same view presets that users create in the UI, enabling use cases like workspace bootstrapping, migration tooling, and automated view setup. In this guide, you’ll learn:

## How views relate to databases and data sources.

## What happens by default when you create a database.

## How to list, create, and delete views.

## How to configure view-specific settings.

## How to create and manage dashboard views.

## How to query data through a view.

## Structure

A **view** is scoped to a single [data source](https://developers.notion.com/reference/data-source) within a [database](https://developers.notion.com/reference/database). It defines how pages in that data source are filtered, sorted, and displayed. The view object looks like this:

```json
{
  "object": "view",
  "id": "a3f1b2c4-5678-4def-abcd-1234567890ab",
  "parent": {
    "type": "database_id",
    "database_id": "248104cd-477e-80fd-b757-e945d38000bd"
  },
  "data_source_id": "248104cd-477e-80af-bc30-000bd28de8f9",
  "name": "High priority items",
  "type": "table",
  "filter": {
    "property": "Priority",
    "select": {
      "equals": "High"
    }
  },
  "sorts": [
    {
      "property": "Last ordered",
      "direction": "descending"
    }
  ],
  "quick_filters": {
    "Status": {
      "status": { "equals": "In progress" }
    }
  },
  "configuration": {
    "type": "table",
    "properties": [
      { "property_id": "title", "visible": true, "width": 300 },
      { "property_id": "abc1", "visible": true, "width": 200 },
      { "property_id": "def2", "visible": false }
    ],
    "group_by": {
      "type": "status",
      "property_id": "ghi3",
      "group_by": "group",
      "sort": { "type": "manual" }
    },
    "wrap_cells": false,
    "frozen_column_index": 1,
    "show_vertical_lines": true
  },
  "created_time": "2026-01-15T10:30:00.000Z",
  "last_edited_time": "2026-01-20T14:22:00.000Z",
  "created_by": {
    "object": "user",
    "id": "e7f3a4b2-1234-5678-9abc-def012345678"
  },
  "last_edited_by": {
    "object": "user",
    "id": "e7f3a4b2-1234-5678-9abc-def012345678"
  },
  "url": "https://www.notion.so/example/248104cd477e80fdb757e945d38000bd?v=a3f1b2c45678"
}
```

Key fields:
- **`type`** — The layout type. One of: `table`, `board`, `list`, `calendar`, `timeline`, `gallery`, `form`, `chart`, `map`, or `dashboard`.
- **`data_source_id`** — Which data source this view is “over”. A database can have multiple data sources, and each view targets exactly one. For dashboard views this is `null` since dashboards contain multiple widget views, each with their own data source.
- **`filter`** and **`sorts`** — Use the same shapes as the [filter](https://developers.notion.com/reference/filter-data-source-entries) and [sort](https://developers.notion.com/reference/sort-data-source-entries) parameters in data source queries.
- **`quick_filters`** — A map of property-level filters that appear in the view’s filter bar. Keys are property names or IDs, values are filter conditions (same shape as property filters, without the `property` field). See [Quick filters](#quick-filters).
- **`configuration`** — Type-specific presentation settings that vary by view type. This is a discriminated union keyed on `type` — see [View configuration](#view-configuration) for the full schema per view type. This field is `null` when no custom configuration has been set.
- **`parent`** — Always a database. Views are retrieved and managed through their parent database.
- **`dashboard_view_id`** — Only present on widget views that belong to a dashboard. References the parent dashboard view’s ID.

## Default behavior

When you [create a database](https://developers.notion.com/reference/create-database) through the API, Notion automatically provisions:
1. One **data source** under the database container
2. One **Table view** named “Default view” over that data source
This means every newly created database is immediately usable — it has a data source to hold pages and a view to display them.

```shellscript
curl -X POST https://api.notion.com/v1/databases \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "parent": { "type": "page_id", "page_id": "YOUR_PAGE_ID" },
    "title": [{ "type": "text", "text": { "content": "My Database" } }],
    "is_inline": false
  }'
```

After creating the database, you can [list the views](#listing-views) to discover the default view, then create additional views as needed.

## Listing views

Use the [list endpoint](https://developers.notion.com/reference/list-views) to discover views. You can filter by the view’s parent `database_id` or by the `data_source_id` that the view references.

### By database

Pass `database_id` to list the views belonging to a specific database block.

```shellscript
curl -X GET "https://api.notion.com/v1/views?database_id=DATABASE_ID" \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"
```

### By data source

Pass `data_source_id` to list all views that reference a given data source (collection), including linked views on other pages across the workspace.

```shellscript
curl -X GET "https://api.notion.com/v1/views?data_source_id=DATA_SOURCE_ID" \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"
```

Results are filtered by your integration’s access permissions. Views on pages the integration cannot access are excluded.

Both variants return a paginated list of view references:

```json
{
  "object": "list",
  "results": [
    { "object": "view", "id": "a3f1b2c4-5678-4def-abcd-1234567890ab" },
    { "object": "view", "id": "b4e2c3d5-6789-5ef0-bcde-2345678901bc" }
  ],
  "next_cursor": null,
  "has_more": false
}
```

The list endpoint returns minimal view references (just `object` and `id`). To get full view details including filters, sorts, and configuration, retrieve each view individually.

## Retrieving a view

[Retrieve a view](https://developers.notion.com/reference/retrieve-a-view) by its ID to see its full configuration, including filters, sorts, and layout settings.

```shellscript
curl -X GET https://api.notion.com/v1/views/VIEW_ID \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"
```

The response is a full [view object](#structure).

## Creating a view

Create a new view by specifying the target data source, a name, and a view type. You must also provide one of `database_id` (to create a top-level view on a database), `view_id` (to add a widget view to an existing dashboard), or `create_database` (to create a linked database view on a page). You can optionally include filters, sorts, and a [configuration](#view-configuration) object. For the full parameter reference, see [Create a view](https://developers.notion.com/reference/create-view).

`database_id` and `data_source_id` are different IDs. The `database_id` is the database container’s ID (the same ID returned by the [Retrieve a database](https://developers.notion.com/reference/retrieve-a-database) endpoint). The `data_source_id` is the ID of a specific data source within that database (found in the database’s `data_sources` array). Most databases have a single data source, but both IDs are required.

```shellscript
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Recent orders",
    "type": "table",
    "filter": {
      "property": "Last ordered",
      "date": {
        "past_week": {}
      }
    },
    "sorts": [
      {
        "property": "Last ordered",
        "direction": "descending"
      }
    ],
    "configuration": {
      "type": "table",
      "properties": [
        { "property_id": "title", "visible": true, "width": 300 },
        { "property_id": "abc1", "visible": true, "width": 200 }
      ],
      "wrap_cells": true
    }
  }'
```

The response is the newly created [view object](#structure) with all fields populated.

Views in a database can be configured to show pages from a data source that’s owned by another database. In Notion, this is called a [linked database](https://www.notion.com/help/data-sources-and-linked-databases) (or linked view), and it’s useful for showing the same underlying data in multiple places—for example, putting filtered views of your Tasks, Projects, and Bugs on a single dashboard page.In the API, the main requirement is that your integration has access to both the database that owns the data source, and the database you’re creating the view in.

**Filtering by multiple select values** To filter a select property by multiple values (e.g. Priority is “Low” or “Medium”), use a compound `or` filter with separate `equals` conditions:

```json
{
  "filter": {
    "or": [
      {
        "property": "Priority",
        "select": { "equals": "Low" }
      },
      {
        "property": "Priority",
        "select": { "equals": "Medium" }
      }
    ]
  }
}
```

The API validates select and status filter values against the property’s configured options. For status properties, group names (e.g. “To-do”, “In progress”, “Complete”) are also accepted. If a value doesn’t match any existing option or group, the API returns a descriptive error listing the available values.

### Required parameters

| Parameter | Description |
| --- | --- |
| `data_source_id` | The ID of the data source this view is over. Retrieve this from the database object’s `data_sources` array. |
| `name` | A display name for the view. |
| `type` | The view layout: `table`, `board`, `list`, `calendar`, `timeline`, `gallery`, `form`, `chart`, `map`, or `dashboard`. |

### Optional parameters

| Parameter | Description |
| --- | --- |
| `database_id` | The ID of the database to create the view in. Mutually exclusive with `view_id` and `create_database`. |
| `view_id` | The ID of a dashboard view to add this view to as a widget. Mutually exclusive with `database_id` and `create_database`. |
| `create_database` | Creates a linked database view on a page referencing an existing data source. See [Creating a linked database view](#creating-a-linked-database-view). Mutually exclusive with `database_id` and `view_id`. |
| `filter` | A [filter object](https://developers.notion.com/reference/filter-data-source-entries) to apply. Uses the same shape as data source queries. |
| `sorts` | An array of [sort objects](https://developers.notion.com/reference/sort-data-source-entries). Uses the same shape as data source queries. |
| `quick_filters` | A map of [quick filters](#quick-filters) for the view’s filter bar. Keys are property names or IDs, values are filter conditions. |
| `configuration` | A [view configuration](#view-configuration) object. The `type` field inside must match the view `type`. |
| `position` | Where to place the new view in the database’s view tab bar. Only applicable when `database_id` is provided. See [View positioning](#view-positioning). Defaults to appending at the end. |
| `placement` | Where to place the new widget in a dashboard layout. Only applicable when `view_id` is provided. See [Widget placement](#widget-placement). Defaults to creating a new row at the end. |

You must provide exactly one of `database_id`, `view_id`, or `create_database`. Use `database_id` to create a top-level view on a database. Use `view_id` to add a widget view to an existing dashboard — see [Dashboard views](#dashboard-views) for details. Use `create_database` to create a linked database view on a page — see [Creating a linked database view](#creating-a-linked-database-view).

**Finding the data source ID** If you already have a database ID, call the [Retrieve a database](https://developers.notion.com/reference/retrieve-database) endpoint. The response includes a `data_sources` array with each data source’s `id` and `name`.

### Creating different view types

Here’s an example of creating a Board view with grouping, cover images, and property configuration:

```shellscript
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Task board",
    "type": "board",
    "configuration": {
      "type": "board",
      "group_by": {
        "type": "status",
        "property_id": "STATUS_PROPERTY_ID",
        "group_by": "group",
        "sort": { "type": "manual" }
      },
      "cover": {
        "type": "page_cover"
      },
      "cover_size": "medium",
      "card_layout": "compact"
    }
  }'
```

### View positioning

When creating a top-level database view (using `database_id`), you can control where it appears in the view tab bar with the `position` parameter. This is a discriminated union on the `type` field:

| Variant | Fields | Description |
| --- | --- | --- |
| `start` | `type` | Places the new view as the first tab. |
| `end` | `type` | Places the new view as the last tab (default). |
| `after_view` | `type`, `view_id` | Places the new view immediately after the specified view. |

```json
{
  "position": { "type": "start" }
}
```

The `position` parameter is only valid when `database_id` is provided. It cannot be used with `view_id` (dashboard widget creation).

### Creating a linked database view

Use the `create_database` parameter to create a lightweight linked database view on a page that references an existing data source. This creates a new database container on the target page with a single view over the specified data source — similar to inserting a “linked view of database” in the Notion UI. This differs from `POST /v1/databases`, which creates a full standalone database with its own schema, data source, and default view. With `create_database`, the view points to an existing data source owned by another database, so no new schema is created.

```javascript
const view = await notion.views.create({
  create_database: {
    parent: {
      type: "page_id",
      page_id: "TARGET_PAGE_ID",
    },
  },
  data_source_id: "EXISTING_DATA_SOURCE_ID",
  name: "Tasks overview",
  type: "table",
});
```

The `create_database` object accepts the following fields:

| Field | Required | Description |
| --- | --- | --- |
| `parent` | Yes | The parent page for the linked database. Must be `{ "type": "page_id", "page_id": "..." }`. |
| `position` | No | Controls where the new database block appears within the parent page. Use `{ "type": "after_block", "block_id": "..." }` to place it after a specific block. The referenced block must be a direct child of the parent page. Defaults to appending at the end. |

All view types are supported with `create_database`, including `form` views with full form configuration and `dashboard` views. Dashboard views are created with an empty layout — add widgets to them via separate `POST /v1/views` calls with `view_id`.

Your integration must have access to both the target page (where the new database container is created) and the database that owns the data source being referenced.

## Updating a view

[Update a view](https://developers.notion.com/reference/update-a-view) to change its name, filters, sorts, or configuration. All fields are optional — only include the fields you want to change.

```shellscript
curl -X PATCH https://api.notion.com/v1/views/VIEW_ID \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "name": "Completed this month",
    "filter": {
      "and": [
        {
          "property": "Status",
          "status": { "equals": "Done" }
        },
        {
          "property": "Completed date",
          "date": { "this_month": {} }
        }
      ]
    },
    "sorts": [
      {
        "property": "Completed date",
        "direction": "descending"
      }
    ],
    "configuration": {
      "type": "table",
      "group_by": null,
      "properties": [
        { "property_id": "title", "visible": true, "width": 400 },
        { "property_id": "abc1", "visible": true },
        { "property_id": "def2", "visible": false }
      ]
    }
  }'
```

To clear a view’s filter, sorts, or specific configuration fields, set them to `null`. See [Clearing configuration with null](#clearing-configuration-with-null) for concrete examples.

## Deleting a view

[Delete a view](https://developers.notion.com/reference/delete-view) by its ID. This permanently removes the view from the database’s view list.

```shellscript
curl -X DELETE https://api.notion.com/v1/views/VIEW_ID \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"
```

The response is a partial view object containing only identity fields (`object`, `id`, `parent`, and `type`). Full view details like filters, sorts, and configuration are not included since the view has been deleted.

Deleting a view cannot be undone through the API. The view will no longer appear in the database’s view list.

A database must always have at least one view. Attempting to delete the last remaining view returns a `validation_error`. To remove the database entirely, set [`in_trash`](https://developers.notion.com/reference/update-database#body-in-trash) to `true` via the update database endpoint instead.

## View configuration

The `configuration` field on a view object controls type-specific presentation settings — things like column widths, grouping, cover images, subtasks, and more. It is a discriminated union keyed on the `type` field, which must match the view’s top-level `type`. You can pass `configuration` when [creating](#creating-a-view) or [updating](#updating-a-view) a view. Nullable fields accept `null` to clear the setting.

### Feature support by view type

| Feature | Table | Board | Calendar | Timeline | Gallery | List | Map | Form | Chart | Dashboard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `properties` | Yes | Yes | Yes | Yes | Yes | Yes | Optional | \- | \- | \- |
| `group_by` | Optional | **Required** | \- | \- | \- | \- | \- | \- | \- | \- |
| `sub_group_by` | \- | Optional | \- | \- | \- | \- | \- | \- | \- | \- |
| `subtasks` | Optional | \- | \- | \- | \- | \- | \- | \- | \- | \- |
| `cover` | \- | Optional | \- | \- | Optional | \- | \- | \- | \- | \- |
| `cover_size` / `cover_aspect` | \- | Optional | \- | \- | Optional | \- | \- | \- | \- | \- |
| `card_layout` | \- | Optional | \- | \- | Optional | \- | \- | \- | \- | \- |
| `date_property_id` | \- | \- | **Required** | **Required** | \- | \- | \- | \- | \- | \- |
| `end_date_property_id` | \- | \- | \- | Optional | \- | \- | \- | \- | \- | \- |
| `view_range` / `show_weekends` | \- | \- | Optional | \- | \- | \- | \- | \- | \- | \- |
| `preference` / `arrows_by` | \- | \- | \- | Optional | \- | \- | \- | \- | \- | \- |
| `show_table` / `table_properties` | \- | \- | \- | Optional | \- | \- | \- | \- | \- | \- |
| `wrap_cells` / `frozen_column_index` | Optional | \- | \- | \- | \- | \- | \- | \- | \- | \- |
| `show_vertical_lines` | Optional | \- | \- | \- | \- | \- | \- | \- | \- | \- |
| `height` | \- | \- | \- | \- | \- | \- | Optional | \- | Optional | \- |
| `map_by` | \- | \- | \- | \- | \- | \- | Optional | \- | \- | \- |
| `is_form_closed` | \- | \- | \- | \- | \- | \- | \- | Optional | \- | \- |
| `anonymous_submissions` | \- | \- | \- | \- | \- | \- | \- | Optional | \- | \- |
| `submission_permissions` | \- | \- | \- | \- | \- | \- | \- | Optional | \- | \- |
| `chart_type` | \- | \- | \- | \- | \- | \- | \- | \- | **Required** | \- |
| `x_axis` / `y_axis` | \- | \- | \- | \- | \- | \- | \- | \- | Optional | \- |
| `value` | \- | \- | \- | \- | \- | \- | \- | \- | Optional | \- |
| `rows` | \- | \- | \- | \- | \- | \- | \- | \- | \- | Yes (read-only) |

### Table configuration

```json
{
  "type": "table",
  "properties": [...],
  "group_by": { ... } | null,
  "subtasks": { ... } | null,
  "wrap_cells": true,
  "frozen_column_index": 1,
  "show_vertical_lines": true
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"table"` | **Required.** Must be `"table"`. |
| `properties` | array \| null | Property visibility and display settings. See [Property configuration](#property-configuration). |
| `group_by` | object \| null | Group rows by a property. See [Group-by configuration](#group-by-configuration). Pass `null` to remove. |
| `subtasks` | object \| null | Sub-item display settings. See [Subtask configuration](#subtask-configuration). Pass `null` to reset to defaults. Use `{ "display_mode": "disabled" }` to explicitly disable. |
| `wrap_cells` | boolean | Whether to wrap cell content. |
| `frozen_column_index` | integer (>= 0) | Number of columns frozen from the left. |
| `show_vertical_lines` | boolean | Whether to show vertical grid lines between columns. |

### Board configuration

```json
{
  "type": "board",
  "group_by": { ... },
  "sub_group_by": { ... } | null,
  "properties": [...],
  "cover": { "type": "page_cover" },
  "cover_size": "medium",
  "cover_aspect": "cover",
  "card_layout": "compact"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"board"` | **Required.** Must be `"board"`. |
| `group_by` | object | **Required.** Group-by configuration for board columns. See [Group-by configuration](#group-by-configuration). |
| `sub_group_by` | object \| null | Secondary group-by for sub-grouping within columns. Pass `null` to remove. |
| `properties` | array \| null | Property visibility on cards. See [Property configuration](#property-configuration). |
| `cover` | object \| null | Cover image source. See [Cover configuration](#cover-configuration). |
| `cover_size` | `"small"` \| `"medium"` \| `"large"` \| null | Size of the cover image on cards. |
| `cover_aspect` | `"contain"` \| `"cover"` \| null | `"contain"` fits the image; `"cover"` fills the area. |
| `card_layout` | `"list"` \| `"compact"` \| null | `"list"` shows full cards; `"compact"` shows condensed cards. |

### Calendar configuration

```json
{
  "type": "calendar",
  "date_property_id": "DATE_PROPERTY_ID",
  "properties": [...],
  "view_range": "month",
  "show_weekends": true
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"calendar"` | **Required.** Must be `"calendar"`. |
| `date_property_id` | string | **Required.** Property ID of the date property used to position items on the calendar. |
| `properties` | array \| null | Property visibility on calendar cards. See [Property configuration](#property-configuration). |
| `view_range` | `"week"` \| `"month"` \| null | Default calendar range. |
| `show_weekends` | boolean \| null | Whether to show weekend days. |

### Timeline configuration

```json
{
  "type": "timeline",
  "date_property_id": "START_DATE_PROPERTY_ID",
  "end_date_property_id": "END_DATE_PROPERTY_ID",
  "properties": [...],
  "show_table": true,
  "table_properties": [...],
  "preference": {
    "zoom_level": "month",
    "center_timestamp": 1706745600000
  },
  "arrows_by": {
    "property_id": "RELATION_PROPERTY_ID"
  },
  "color_by": true
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"timeline"` | **Required.** Must be `"timeline"`. |
| `date_property_id` | string | **Required.** Property ID for the start date of timeline items. |
| `end_date_property_id` | string \| null | Property ID for the end date. Pass `null` to clear. |
| `properties` | array \| null | Property visibility on timeline items. See [Property configuration](#property-configuration). |
| `show_table` | boolean \| null | Whether to show the table panel alongside the timeline. |
| `table_properties` | array \| null | Property configuration for the table panel (when `show_table` is true). |
| `preference` | object \| null | Timeline display preferences. See below. |
| `arrows_by` | object \| null | Dependency arrow configuration. See below. |
| `color_by` | boolean \| null | Whether to color timeline items by a property. |

**Timeline preference object:**

| Field | Type | Description |
| --- | --- | --- |
| `zoom_level` | enum | **Required.** One of: `"hours"`, `"day"`, `"week"`, `"bi_week"`, `"month"`, `"quarter"`, `"year"`, `"5_years"`. |
| `center_timestamp` | integer | Timestamp in milliseconds to center the timeline on. |

**Timeline arrows\_by object:**

| Field | Type | Description |
| --- | --- | --- |
| `property_id` | string \| null | Relation property ID for dependency arrows, or `null` to disable arrows. |

### Gallery configuration

```json
{
  "type": "gallery",
  "properties": [...],
  "cover": { "type": "page_content" },
  "cover_size": "large",
  "cover_aspect": "cover",
  "card_layout": "list"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"gallery"` | **Required.** Must be `"gallery"`. |
| `properties` | array \| null | Property visibility on gallery cards. See [Property configuration](#property-configuration). |
| `cover` | object \| null | Cover image source. See [Cover configuration](#cover-configuration). |
| `cover_size` | `"small"` \| `"medium"` \| `"large"` \| null | Size of the cover image on cards. |
| `cover_aspect` | `"contain"` \| `"cover"` \| null | `"contain"` fits the image; `"cover"` fills the area. |
| `card_layout` | `"list"` \| `"compact"` \| null | `"list"` shows full cards; `"compact"` shows condensed cards. |

### List configuration

```json
{
  "type": "list",
  "properties": [...]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"list"` | **Required.** Must be `"list"`. |
| `properties` | array \| null | Property visibility and display settings. See [Property configuration](#property-configuration). |

### Map configuration

```json
{
  "type": "map",
  "height": "medium",
  "map_by": "LOCATION_PROPERTY_ID",
  "properties": [...]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"map"` | **Required.** Must be `"map"`. |
| `height` | `"small"` \| `"medium"` \| `"large"` \| `"extra_large"` \| null | Map display height. Pass `null` to clear. |
| `map_by` | string \| null | Property ID of the location property used to position items on the map. Pass `null` to clear. |
| `properties` | array \| null | Property visibility on map pin cards. See [Property configuration](#property-configuration). |

In responses, an additional read-only field `map_by_property_name` may be present, containing the display name of the `map_by` property.

### Form configuration

```json
{
  "type": "form",
  "is_form_closed": false,
  "anonymous_submissions": true,
  "submission_permissions": "comment_only"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"form"` | **Required.** Must be `"form"`. |
| `is_form_closed` | boolean \| null | Whether the form is closed for submissions. Pass `null` to clear. |
| `anonymous_submissions` | boolean \| null | Whether anonymous (non-logged-in) submissions are allowed. Pass `null` to clear. |
| `submission_permissions` | `"none"` \| `"comment_only"` \| `"reader"` \| `"read_and_write"` \| `"editor"` \| null | Permission level granted to the submitter on the created page after form submission. Pass `null` to clear. |

### Chart configuration

Chart views display database data as visual charts. The configuration uses a flat object with `chart_type` as a required discriminator. Available fields vary by chart type.

```json
{
  "type": "chart",
  "chart_type": "column",
  "x_axis": {
    "type": "select",
    "property_id": "CATEGORY_PROP_ID",
    "sort": { "type": "manual" }
  },
  "y_axis": {
    "aggregator": "sum",
    "property_id": "AMOUNT_PROP_ID"
  },
  "color_theme": "blue",
  "color_by_value": true,
  "show_data_labels": true,
  "height": "medium"
}
```

When `color_by_value` is enabled on a bar or column chart, each bar is shaded along a gradient based on its numeric value — higher values appear in a darker shade and lower values in a lighter shade. This is useful for quickly spotting relative magnitude across categories. Combine with `color_theme` to control the gradient’s base color. **Required fields:**

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"chart"` | **Required.** Must be `"chart"`. |
| `chart_type` | `"column"` \| `"bar"` \| `"line"` \| `"donut"` \| `"number"` | **Required.** The chart type: `"column"` (vertical bars), `"bar"` (horizontal bars), `"line"`, `"donut"`, or `"number"` (single value display). |

**Data configuration fields:** Charts support two data modes: **grouped data** (aggregate values by grouping on a property) and **results** (use raw property values directly).

| Field | Type | Description |
| --- | --- | --- |
| `x_axis` | object \| null | X-axis grouping configuration for column/bar/line/donut charts using grouped data. Uses the same [group-by configuration](#group-by-configuration) shape. Null when using results mode. Pass `null` to clear. |
| `y_axis` | object \| null | Y-axis [aggregation](#chart-aggregation) for column/bar/line/donut charts using grouped data. Null when using results mode. Pass `null` to clear. |
| `x_axis_property_id` | string \| null | Property ID for x-axis name values when using results (raw property values) mode. Pass `null` to clear. |
| `y_axis_property_id` | string \| null | Property ID for y-axis numeric values when using results mode. Pass `null` to clear. |
| `value` | object \| null | [Aggregation](#chart-aggregation) configuration for number charts (single value display). Pass `null` to clear. |
| `stack_by` | object \| null | Stack-by grouping configuration for stacked/grouped charts (column/bar/line only). Uses the same [group-by configuration](#group-by-configuration) shape. Pass `null` to clear. |

**Format fields (all optional, all nullable):**

| Field | Type | Description |
| --- | --- | --- |
| `sort` | `"manual"` \| `"x_ascending"` \| `"x_descending"` \| `"y_ascending"` \| `"y_descending"` | Sort order for chart data. |
| `color_theme` | `"gray"` \| `"blue"` \| `"yellow"` \| `"green"` \| `"purple"` \| `"teal"` \| `"orange"` \| `"pink"` \| `"red"` \| `"auto"` \| `"colorful"` | Color theme. |
| `height` | `"small"` \| `"medium"` \| `"large"` \| `"extra_large"` | Chart height. |
| `hide_empty_groups` | boolean | Whether to hide groups with no data on the x-axis. |
| `legend_position` | `"off"` \| `"bottom"` \| `"side"` | Legend display position. `"off"` hides the legend. |
| `show_data_labels` | boolean | Whether to show data value labels on chart elements. |
| `color_by_value` | boolean | Whether to apply gradient coloring to chart elements based on their numeric value. Higher values appear in a darker shade and lower values in a lighter shade. |
| `axis_labels` | `"none"` \| `"x_axis"` \| `"y_axis"` \| `"both"` | Which axis labels to display. |
| `grid_lines` | `"none"` \| `"horizontal"` \| `"vertical"` \| `"both"` | Which grid lines to display. |
| `y_axis_min` | number \| null | Custom minimum value for the y-axis. |
| `y_axis_max` | number \| null | Custom maximum value for the y-axis. |
| `reference_lines` | array \| null | [Reference lines](#chart-reference-lines) drawn on the chart. |
| `caption` | string \| null | Text caption displayed below the chart. |

**Line-specific fields:**

| Field | Type | Description |
| --- | --- | --- |
| `cumulative` | boolean | Whether to show cumulative values. |
| `smooth_line` | boolean | Whether to use smooth curves. |
| `hide_line_fill_area` | boolean | Whether to hide the shaded area under the line. |

**Bar/column-specific fields:**

| Field | Type | Description |
| --- | --- | --- |
| `group_style` | `"normal"` \| `"percent"` \| `"side_by_side"` | How grouped/stacked bars are displayed. `"normal"` stacks values, `"percent"` normalizes to 100%, `"side_by_side"` places bars next to each other. |

**Donut-specific fields:**

| Field | Type | Description |
| --- | --- | --- |
| `donut_labels` | `"none"` \| `"value"` \| `"name"` \| `"name_and_value"` | What to display on donut chart slices. |

**Number-specific fields:**

| Field | Type | Description |
| --- | --- | --- |
| `hide_title` | boolean | Whether to hide the title label. |

#### Chart aggregation

The `y_axis` and `value` fields use an aggregation object:

```json
{
  "aggregator": "sum",
  "property_id": "AMOUNT_PROP_ID"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `aggregator` | enum | **Required.** The aggregation operator. `"count"` counts all rows and does not require a `property_id`. All other operators require a `property_id`. |
| `property_id` | string | The property to aggregate on. Required for all operators except `"count"`. |

**Supported aggregation operators:** `count`, `count_values`, `sum`, `average`, `median`, `min`, `max`, `range`, `unique`, `empty`, `not_empty`, `percent_empty`, `percent_not_empty`, `checked`, `unchecked`, `percent_checked`, `percent_unchecked`, `earliest_date`, `latest_date`, `date_range`.

#### Chart reference lines

Reference lines are horizontal lines drawn at specific y-axis values for visual comparison:

```json
{
  "id": "ref-line-1",
  "value": 100,
  "label": "Target",
  "color": "red",
  "dash_style": "dash"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier for the reference line. Auto-generated if omitted when creating. |
| `value` | number | **Required.** The y-axis value where the reference line is drawn. |
| `label` | string | **Required.** Label displayed alongside the reference line. |
| `color` | enum | **Required.** Color of the reference line. One of: `"gray"`, `"lightgray"`, `"brown"`, `"yellow"`, `"orange"`, `"green"`, `"blue"`, `"purple"`, `"pink"`, `"red"`. |
| `dash_style` | `"solid"` \| `"dash"` | **Required.** Line style: `"solid"` for a continuous line, `"dash"` for a dashed line. |

### Dashboard configuration

```json
{
  "type": "dashboard",
  "rows": [
    {
      "id": "row-id-1",
      "widgets": [
        { "id": "widget-id-1", "view_id": "VIEW_ID_1", "width": 6, "row_index": 0 },
        { "id": "widget-id-2", "view_id": "VIEW_ID_2", "width": 6, "row_index": 0 }
      ],
      "height": 400
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | `"dashboard"` | **Required.** Must be `"dashboard"`. |
| `rows` | array | **Required.** The rows that make up the dashboard layout. Each row contains one or more widget modules. |

**Dashboard row object:**

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | The ID of this row module. |
| `widgets` | array | The widget modules within this row. |
| `height` | integer | Fixed height of the row in pixels. |

**Dashboard widget object:**

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | The ID of this widget module. |
| `view_id` | string | The ID of the collection view rendered by this widget. |
| `width` | integer | Width of the widget in a 12-column grid (1–12). `12` means full width. |
| `row_index` | integer | The 0-based index of the row this widget belongs to. Widgets in the same row share the same `row_index`. |

Dashboard configuration is **read-only** — it is returned when retrieving a dashboard view but cannot be set directly when creating or updating a view. The layout structure is managed by creating and deleting widget views via the `view_id` parameter on the create endpoint.

### Property configuration

The `properties` array controls which database properties are visible in the view and how they are displayed. Each entry targets a single property by its ID or name.

```json
{
  "property_id": "abc1",
  "visible": true,
  "width": 200,
  "wrap": true,
  "date_format": "relative",
  "time_format": "12_hour"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `property_id` | string | **Required.** The property ID or property name. When a name is provided, the API resolves it to the corresponding property ID. If the string matches both a property ID and a different property’s name, the ID match takes priority. |
| `visible` | boolean | Whether the property is visible in this view. |
| `width` | integer (>= 0) | Column width in pixels (table views only). |
| `wrap` | boolean | Whether to wrap content in this property cell or card. |
| `status_show_as` | `"select"` \| `"checkbox"` | How to display status properties. |
| `card_property_width_mode` | `"full_line"` \| `"inline"` | Property width mode in compact card layouts (board/gallery). |
| `date_format` | enum | Display format for date properties. One of: `"full"`, `"short"`, `"month_day_year"`, `"day_month_year"`, `"year_month_day"`, `"relative"`. |
| `time_format` | enum | Time display format for date properties. One of: `"12_hour"`, `"24_hour"`, `"hidden"`. |

### Group-by configuration

Group-by lets you organize rows or cards into sections based on a property’s values. The shape varies by property type, forming a discriminated union on the `type` field. All group-by variants share these fields:

| Field | Type | Description |
| --- | --- | --- |
| `type` | string | **Required.** The property type being grouped. Determines which additional fields are available. |
| `property_id` | string | **Required.** The property ID to group by. |
| `sort` | object | **Required.** Sort order for the groups. An object with `type`: `"manual"`, `"ascending"`, or `"descending"`. |
| `hide_empty_groups` | boolean | Whether to hide groups with no items. |

The following table shows which `type` values are supported and what extra fields each variant accepts:

| `type` value(s) | Extra required fields | Extra optional fields |
| --- | --- | --- |
| `select`, `multi_select` | — | — |
| `status` | `group_by`: `"group"` (by status group: To Do/In Progress/Done) or `"option"` (by individual option) | — |
| `person`, `created_by`, `last_edited_by` | — | — |
| `relation` | — | — |
| `date`, `created_time`, `last_edited_time` | `group_by`: `"relative"` \| `"day"` \| `"week"` \| `"month"` \| `"year"` | `start_day_of_week`: `0` (Sunday) or `1` (Monday) |
| `text`, `title`, `url`, `email`, `phone_number` | `group_by`: `"exact"` or `"alphabet_prefix"` (first letter) | — |
| `number` | — | `range_start`, `range_end`, `range_size` (>= 1) for bucket grouping |
| `checkbox` | — | — |
| `formula` | `group_by`: a nested sub-group-by object (see below) | — |

**Formula group-by** uses a nested `group_by` object that describes how to group the formula’s result type. The nested object does not include `property_id` (it inherits from the parent). Supported formula result types:

| Result type | Nested `group_by` fields |
| --- | --- |
| `date` | `type`, `group_by` (`"relative"` \| `"day"` \| `"week"` \| `"month"` \| `"year"`), `sort`, optionally `start_day_of_week` |
| `text` | `type`, `group_by` (`"exact"` \| `"alphabet_prefix"`), `sort` |
| `number` | `type`, `sort`, optionally `range_start`, `range_end`, `range_size` |
| `checkbox` | `type`, `sort` |

```json
{
  "type": "select",
  "property_id": "PRIORITY_PROPERTY_ID",
  "sort": { "type": "manual" },
  "hide_empty_groups": true
}
```

### Subtask configuration

Subtask (sub-item) configuration controls how parent-child relationships are displayed in table views. This uses a self-referencing relation property to establish hierarchy.

```json
{
  "property_id": "RELATION_PROPERTY_ID",
  "display_mode": "show",
  "filter_scope": "parents_and_subitems",
  "toggle_column_id": "title"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `property_id` | string | Relation property ID used for parent-child nesting. |
| `display_mode` | enum | How sub-items are displayed. One of: `"show"` (hierarchical with toggles), `"hidden"` (parents with a count), `"flattened"` (sub-items with a parent indicator), `"disabled"` (no sub-item rendering). |
| `filter_scope` | enum | Which items are included when filtering. One of: `"parents"` (parent items only), `"parents_and_subitems"` (both), `"subitems"` (sub-items only). |
| `toggle_column_id` | string | Property ID of the column showing the expand/collapse toggle. |

### Cover configuration

Cover configuration controls the image displayed at the top of each card in board and gallery views.

```json
{
  "type": "page_cover",
}
```

| Field | Type | Description |
| --- | --- | --- |
| `type` | enum | **Required.** Source of the cover image. One of: `"page_cover"` (the page’s cover image), `"page_content"` (first image in page content), `"property"` (an image from a file property). |
| `property_id` | string | Property ID to use as the cover image source. Only used when `type` is `"property"`. |

### Clearing configuration with null

When updating a view, you can pass `null` for any nullable configuration field to remove that setting. Only include the fields you want to change — omitted fields are left unchanged. Here are common scenarios:

```javascript
// A table view currently has group_by set.
// Pass null to remove grouping and return to a flat table.
const updated = await notion.views.update({
  view_id: "VIEW_ID",
  configuration: {
    type: "table",
    group_by: null,
  },
});
```

Configuration updates use **shallow merge** — only the fields you include are changed, and omitted optional fields are preserved. The `configuration` field itself is optional (omit it to leave config unchanged). When present, you must include `type` and any fields marked as required for that view type (e.g., board views always require `group_by`, calendar/timeline views always require `date_property_id`). See [Feature support by view type](#feature-support-by-view-type) for which fields are required vs optional per view type.

## Quick filters

Quick filters appear in the view’s filter bar and let users quickly toggle property-level filters without opening the full filter panel. In the API, `quick_filters` is a map where keys are property names or IDs, and values are filter conditions using the same shape as [property filters](https://developers.notion.com/reference/filter-data-source-entries) but without the `property` field. People filters accept `"me"` as a value for `contains` and `does_not_contain` to match the current user, so you can create filters like “assigned to me” without hardcoding a user ID.

### Adding quick filters on create

```javascript
const view = await notion.views.create({
  database_id: "DATABASE_ID",
  data_source_id: "DATA_SOURCE_ID",
  name: "Active tasks",
  type: "table",
  quick_filters: {
    "Status": {
      status: { equals: "In progress" },
    },
    "Priority": {
      select: { equals: "High" },
    },
  },
});
```

### Adding or updating a quick filter

To add a new quick filter or update an existing one, include the property key with the new filter condition. Other existing quick filters are preserved.

```javascript
const view = await notion.views.update({
  view_id: "VIEW_ID",
  quick_filters: {
    "Assignee": {
      people: { contains: "me" },
    },
  },
});
```

### Removing a quick filter

Set a specific quick filter to `null` to remove it from the filter bar. Other quick filters are preserved.

```javascript
const view = await notion.views.update({
  view_id: "VIEW_ID",
  quick_filters: {
    "Status": null,
  },
});
```

### Clearing all quick filters

Set the entire `quick_filters` field to `null` to remove all quick filters from the view.

```javascript
const view = await notion.views.update({
  view_id: "VIEW_ID",
  quick_filters: null,
});
```

## Dashboard views

Dashboard views let you arrange multiple widget views in a grid layout on a single database. Each widget is itself a view (table, board, list, etc.) that can reference a different data source.

### Creating a dashboard

Create a dashboard view the same way as any other view — pass `type: "dashboard"` with a `database_id`:

```shellscript
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2025-09-03" \
  --data '{
    "database_id": "DATABASE_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Project overview",
    "type": "dashboard"
  }'
```

### Adding widget views

To add a widget to a dashboard, create a view with `view_id` set to the dashboard’s ID instead of `database_id`. Each widget can use a different `data_source_id`. Dashboards support all view types as widgets except for other dashboards (no nested dashboards).

```shellscript
curl -X POST https://api.notion.com/v1/views \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2025-09-03" \
  --data '{
    "view_id": "DASHBOARD_VIEW_ID",
    "data_source_id": "DATA_SOURCE_ID",
    "name": "Tasks by status",
    "type": "board",
    "configuration": {
      "type": "board",
      "group_by": {
        "type": "status",
        "property_id": "STATUS_PROPERTY_ID",
        "group_by": "group",
        "sort": { "type": "manual" }
      }
    }
  }'
```

### Widget placement

When adding a widget to a dashboard, you can control where it appears in the layout using the `placement` parameter. This is a discriminated union on the `type` field:

| Variant | Fields | Description |
| --- | --- | --- |
| `new_row` | `type`, optional `row_index` | Creates a new row containing the widget. If `row_index` is omitted, the new row is appended at the end. If provided, the new row is inserted at that 0-based position. |
| `existing_row` | `type`, `row_index` (required) | Adds the widget side-by-side to an existing row at the specified 0-based index. Column widths are automatically redistributed. |

```json
{
  "placement": { "type": "new_row" }
}
```

The `placement` parameter is only valid when `view_id` is provided (dashboard widget creation). It cannot be used with `database_id`. Each dashboard row supports a maximum of 4 widgets.

### Retrieving a dashboard

When you retrieve a dashboard view, its `configuration` contains the full layout structure — rows of widgets with their positions and sizes:

```json
{
  "object": "view",
  "id": "DASHBOARD_VIEW_ID",
  "type": "dashboard",
  "configuration": {
    "type": "dashboard",
    "rows": [
      {
        "id": "row-1",
        "widgets": [
          { "id": "widget-1", "view_id": "VIEW_ID_1", "width": 6, "row_index": 0 },
          { "id": "widget-2", "view_id": "VIEW_ID_2", "width": 6, "row_index": 0 }
        ]
      }
    ]
  }
}
```

Widget views include a `dashboard_view_id` field that references their parent dashboard. Their `parent.database_id` always resolves to the underlying database, even though they are positioned inside a dashboard layout.

### Deleting widget views

Delete a widget view using the standard delete endpoint. This also removes the widget from the dashboard’s layout structure.

Dashboard views cannot be nested — you cannot create a dashboard widget inside another dashboard.

## Querying a view

Use a view query to fetch pages using the view’s saved filter and sort configuration. This lets integrations reproduce what a user sees in the Notion UI for a particular view, without needing to manually reconstruct the filter/sort logic. View queries use a three-step pattern:
1. **Create a query** — executes the view’s filters/sorts and returns the first page of results along with a `query_id`.
2. **Paginate results** — use the `query_id` to fetch additional pages from the cached result set.
3. **Delete the query** (recommended) — free the cached result set when you’re done paginating.

### Step 1: Create a view query

```shellscript
curl -X POST https://api.notion.com/v1/views/VIEW_ID/queries \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2026-03-11" \
  --data '{
    "page_size": 50
  }'
```

The response includes the first page of results inline:

```json
{
  "object": "view_query",
  "id": "query-id-here",
  "view_id": "VIEW_ID",
  "expires_at": "2026-01-20T14:37:00.000Z",
  "total_count": 128,
  "results": [
    { "object": "page", "id": "..." }
  ],
  "next_cursor": "cursor-string",
  "has_more": true
}
```

### Step 2: Paginate results

```shellscript
curl -X GET "https://api.notion.com/v1/views/VIEW_ID/queries/QUERY_ID?start_cursor=CURSOR&page_size=50" \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"
```

Once you’ve finished paginating, delete the query to free the cached result set. This is optional — queries expire automatically after approximately 15 minutes — but recommended as good practice, especially if your integration runs queries frequently.

```shellscript
curl -X DELETE "https://api.notion.com/v1/views/VIEW_ID/queries/QUERY_ID" \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H "Notion-Version: 2026-03-11"
```

The response confirms deletion:

```json
{
  "object": "view_query",
  "id": "QUERY_ID",
  "deleted": true
}
```

This endpoint is idempotent — calling it on an already-deleted or expired query still returns success.

**Query expiration** Cached query results expire after a short TTL (approximately 15 minutes). If a query expires, create a new one. This caching approach provides stable pagination — results won’t shift between pages due to concurrent data changes.

View queries do not support stacking additional filters or sorts on top of the saved view definition. If you need different filter/sort criteria, create a new view (or update an existing one) and query that instead.

## Permissions

View endpoints reuse existing database [integration capabilities](https://developers.notion.com/reference/capabilities):

| Operation | Required capability |
| --- | --- |
| List views | `read_content` or `read_property` |
| Retrieve a view | `read_content` or `read_property` |
| Create a view | `insert_content`, `insert_property`, `update_content`, or `update_property` |
| Update a view | `update_content` or `update_property` |
| Delete a view | `update_content` or `update_property` |
| Query a view (create, paginate, delete) | `read_content` or `read_property` |

The integration must also have access to the parent database. If it doesn’t, the API returns a `404` rather than a `403`.
- Explore the [database object](https://developers.notion.com/reference/database) and [data source object](https://developers.notion.com/reference/data-source) reference docs for the parent resources that views live under.
- Learn about [filters](https://developers.notion.com/reference/filter-data-source-entries) and [sorts](https://developers.notion.com/reference/sort-data-source-entries) — these shapes are shared between data source queries and view configuration.
- Review [Working with databases](https://developers.notion.com/guides/data-apis/working-with-databases) for a broader overview of database concepts.
- See [Programmatic workspace setup](https://developers.notion.com/guides/data-apis/workspace-setup-for-public-integrations) to learn how public integrations can combine views, databases, and templates to build workspace content for users.