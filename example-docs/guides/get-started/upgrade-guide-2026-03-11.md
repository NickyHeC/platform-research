Notion API version `2026-03-11` introduces three breaking changes that affect block operations, trash/archive semantics, and the [`transcription` block type](https://developers.notion.com/reference/block#transcription). Most integrations will need only minor find-and-replace updates.

**Breaking changes** If your integration uses any of the following, it will break when you upgrade to `2026-03-11`:
- The `after` parameter in [Append block children](https://developers.notion.com/reference/patch-block-children)
- The `archived` field in any request or response
- The [`transcription` block type](https://developers.notion.com/reference/block#transcription)

## What’s changing

| Change | Before (`2025-09-03`) | After (`2026-03-11`) |
| --- | --- | --- |
| **Block positioning** | `after` string parameter | `position` object (`after_block`, `start`, `end`) |
| **Trash status** | `archived` field | `in_trash` field |
| **Block type rename** | [`transcription`](https://developers.notion.com/reference/block#transcription) block type | `meeting_notes` block type |

## Upgrade checklist

## Step-by-step guide

### Step 1: Replace after with position

The [Append block children](https://developers.notion.com/reference/patch-block-children) endpoint no longer accepts a flat `after` parameter. Instead, use the `position` object to specify where new blocks should be inserted. The `position` object supports three placement types:
- `after_block` — insert after a specific block (replaces the old `after` parameter)
- `start` — insert at the beginning of the parent
- `end` — insert at the end of the parent (the default when `position` is omitted)

```json
// PATCH /v1/blocks/{block_id}/children
// Notion-Version: 2026-03-11
{
  "position": {
    "type": "after_block",
    "after_block": { "id": "b5d8fd79-..." }
  },
  "children": [
    {
      "paragraph": {
        "rich_text": [{ "text": { "content": "New paragraph" } }]
      }
    }
  ]
}
```

### Step 2: Replace archived with in\_trash

The `archived` field has been renamed to `in_trash` across all API responses and request parameters. This applies to pages, databases, blocks, and data sources. The `archived` field was [deprecated in April 2024](https://developers.notion.com/page/changelog#changes-for-april-2024). If your integration already reads `in_trash` from responses, you only need to update your request parameters.

#### Response bodies

```json
{
  "object": "page",
  "id": "59b8df07-...",
  "in_trash": false,
  "created_time": "2025-08-07T10:11:07.504Z",
  "last_edited_time": "2025-08-10T15:53:11.386Z",
  "parent": {
    "type": "page_id",
    "page_id": "255104cd-..."
  },
  "properties": {}
}
```

#### Request parameters

For example, when trashing a page:

```json
// PATCH /v1/pages/{page_id}
// Notion-Version: 2026-03-11
{
  "in_trash": true
}
```

Update both your request bodies and any code that reads `archived` from responses to use `in_trash` instead.

### Step 3: Replace transcription with meeting\_notes

The [`transcription`](https://developers.notion.com/reference/block#transcription) block type has been renamed to `meeting_notes`. Update any code that creates, reads, or filters by this block type.

```json
{
  "object": "block",
  "id": "a1c2d3e4-...",
  "type": "meeting_notes",
  "meeting_notes": {
    "rich_text": [
      { "text": { "content": "Meeting transcript content..." } }
    ]
  },
  "created_time": "2025-10-01T12:00:00.000Z",
  "last_edited_time": "2025-10-01T12:30:00.000Z",
  "in_trash": false
}
```

If your integration filters blocks by type, update any `type === "transcription"` checks to use `"meeting_notes"`.

### Step 4: Upgrade the JS/TS SDK (if applicable)

**`@notionhq/client` v5.12.0** of the SDK adds backwards-compatible support for API version `2026-03-11`. All old fields and types are preserved with `@deprecated` annotations — no breaking changes.

To opt in to the new version:

```typescript
import { Client } from "@notionhq/client"

const notion = new Client({
  auth: process.env.NOTION_ACCESS_TOKEN,
  notionVersion: "2026-03-11",
})
```

The SDK’s TypeScript types include both the old and new field names during the transition period. The old names (`archived`, `after`, `transcription`) are marked `@deprecated` to help you find code that needs updating.

### Database automation webhooks

If you use database automation webhooks (the “Send webhook” action in Notion automations), Notion will display an upgrade banner in the automation editor when a webhook action uses an older API version. You can upgrade individual webhook actions to `2026-03-11` using the “Upgrade to latest version” button, or leave them on `2025-09-03` for backward compatibility. New webhook actions will default to `2026-03-11` going forward.

### Integration webhooks

API version `2026-03-11` is now available as an [integration webhook](https://developers.notion.com/reference/webhooks) subscription version. While there are no changes to webhook event payloads in this version (the `archived → in_trash` rename only applies to REST API request/response bodies, not webhook payloads), we recommend upgrading your webhook subscription version to `2026-03-11` to keep it in sync with your API version. To upgrade your webhook subscription version:

This is a no-op upgrade — webhook event payloads are identical between `2025-09-03` and `2026-03-11`. The new version is provided for consistency with the REST API version.