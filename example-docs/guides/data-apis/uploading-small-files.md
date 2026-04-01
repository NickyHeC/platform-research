The **Direct Upload** method lets you securely upload private files to Notion-managed storage via the API. Once uploaded, these files can be reused and attached to pages, blocks, or database properties. This guide walks you through the upload lifecycle:

**Tip**:Upload once, attach many times. You can reuse the same `file_upload` ID across multiple blocks or pages.

## Step 1 - Create a File Upload object

Before uploading any content, start by creating a [File Upload object](https://developers.notion.com/reference/file-upload). This returns a unique `id` and `upload_url` used to send the file.

**Tip:**Save the `id` — You’ll need it to upload the file in Step 2 and attach it in Step 3.

### Example requests

This snippet sends a `POST` request to create the upload object.

```text
curl --request POST \
  --url 'https://api.notion.com/v1/file_uploads' \
  -H 'Authorization: Bearer ntn_****' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2026-03-11' \
  --data '{}'
```

### Example Response

```json
{
  "object": "file_upload",
  "id": "a3f9d3e2-1abc-42de-b904-badc0ffee000",
  "created_time": "2025-04-09T22:26:00.000Z",
  "last_edited_time": "2025-04-09T22:26:00.000Z",
  "expiry_time": "2025-04-09T23:26:00.000Z",
  "upload_url": "https://api.notion.com/v1/file_uploads/a3f9d3e2-1abc-42de-b904-badc0ffee000/send",
  "archived": false,
  "status": "pending",
  "filename": null,
  "content_type": null,
  "content_length": null,
  "request_id": "b7c1fd7e-2c84-4f55-877e-d3ad7db2ac4b"
}
```

## Step 2 - Upload file contents

Next, use the `upload_url` or File Upload object `id` from Step 1 to send the binary file contents to Notion.

**Tips**:
- The only required field is the file contents under the `file` key.
- Unlike other Notion APIs, the Send File Upload endpoint expects a Content-Type of multipart/form-data, not application/json.
- Include a boundary in the `Content-Type` header \[for the Send File Upload API\] as described in [RFC 2388](https://datatracker.ietf.org/doc/html/rfc2388) and [RFC 1341](https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html). Most HTTP clients (e.g. `fetch`, `ky`) handle this automatically if you include `FormData` with your file and don’t pass an explicit `Content-Type` header.

### Example requests

This uploads the file directly from your local system.

```shellscript
curl --request POST \
  --url 'https://api.notion.com/v1/file_uploads/a3f9d3e2-1abc-42de-b904-badc0ffee000/send' \
  -H 'Authorization: Bearer ntn_****' \
  -H 'Notion-Version: 2026-03-11' \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@path/to-file.gif"
```

### Example response

```json
{
  "object": "file_upload",
  "id": "a3f9d3e2-1abc-42de-b904-badc0ffee000",
  "created_time": "2025-04-09T22:26:00.000Z",
  "last_edited_time": "2025-04-09T22:27:00.000Z",
  "expiry_time": "2025-04-09T23:26:00.000Z",
  "archived": false,
  "status": "uploaded",
  "filename": "Really funny.gif",
  "content_type": "image/gif",
  "content_length": "4435",
  "request_id": "91a4ee8c-61f6-4c27-bd41-09aa35299929"
}
```

**Reminder:**Files must be attached within **1 hour** of upload or they’ll be automatically moved to an `archived` status.

## Step 3 - Attach the file to a page or block

Once the file’s `status` is `uploaded`, it can be attached to any location that supports file objects using the File Upload object `id`. This step uses standard Notion API endpoints; there’s no special upload-specific API for attaching. Just pass a file object with a type of `file_upload` and include the `id` that you received earlier in Step 1. You can use the file upload `id` with the following APIs:

### Example: add an image block to a page

This example uses the [Append block children](https://developers.notion.com/reference/patch-block-children) API to create a new image block in a page and attach the uploaded file.

```shellscript
curl --request PATCH \
    --url "https://api.notion.com/v1/blocks/$PAGE_OR_BLOCK_ID/children" \
    -H "Authorization: Bearer ntn_*****" \
    -H 'Content-Type: application/json' \
    -H 'Notion-Version: 2026-03-11' \
    --data '{
        "children": [
            {
                "type": "image",
                "image": {
                    "caption": [],
                    "type": "file_upload",
                    "file_upload": {
                        "id": "'"$FILE_UPLOAD_ID'""
                    }
                }
            }
        ]
    }'
```

### Example: add a file block to a page

example uses the [Append block children](https://developers.notion.com/reference/patch-block-children) API to create a new file block in a page and attach the uploaded file.

```shellscript
curl --request PATCH \
  --url "https://api.notion.com/v1/blocks/$PAGE_OR_BLOCK_ID/children" \
  -H "Authorization: Bearer ntn_*****" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2026-03-11' \
  --data '{
      "children": [
          {
              "type": "file",
              "file": {
                  "type": "file_upload",
                  "file_upload": {
                      "id": "'"$FILE_UPLOAD_ID"'"
                  }
              }
          }
      ]
  }'
```

### Example: attach a file property to a page in a database

This example uses the [Update page](https://developers.notion.com/reference/patch-page) API to ad the uploaded file to a `files` property on a page that lives in a Notion database.

```shellscript
curl --request PATCH \
  --url "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H 'Authorization: Bearer ntn_****' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2026-03-11' \
  --data '{
    "properties": {
      "Attachments": {
        "type": "files",
        "files": [
          {
            "type": "file_upload",
            "file_upload": { "id": "9a8b7c6d-1e2f-4a3b-9e0f-a1b2c3d4e5f6" },
            "name": "logo.png"
          }
        ]
      }
    }
  }'
```

### Example: Set a page cover

This example uses the [Update page](https://developers.notion.com/reference/patch-page) API to add the uploaded file as a page cover.

```shellscript
curl --request PATCH \
  --url "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H 'Authorization: Bearer ntn_****' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2026-03-11' \
  --data '{
      "cover": {
          "type": "file_upload",
          "file_upload": {
              "id": "'"$FILE_UPLOAD_ID"'"
          }
      }
  }'
```

**You’ve successfully uploaded and attached a file using Notion’s Direct Upload method.**

## File lifecycle and reuse

When a file is first uploaded, it has an `expiry_time`, one hour from the time of creation, during which it must be attached. Once attached to any page, block, or database in your workspace:
- The `expiry_time` is removed.
- The file becomes a permanent part of your workspace.
- The `status` remains `uploaded`.
Even if the original content is deleted, the `file_upload` ID remains valid and can be reused to attach the file again. Currently, there is no way to delete or revoke a file upload after it has been created. Attaching a file upload gives you access to a temporary download URL via the Notion API. These URLs expire after 1 hour. To refresh access, re-fetch the page, block, or database where the file is attached.

**Tip:**A file becomes persistent and reusable after the first successful attachment — no need to re-upload.

## Tips and troubleshooting

- **URL expiration**: Notion-hosted files expire after 1 hour. Always re-fetch file objects to refresh links.
- **Attachment deadline**: Files must be attached within 1 hour of upload, or they’ll expire.
- **Size limit**: This guide only supports files up to 20 MB. Larger files require a [multi-part upload](https://developers.notion.com/guides/data-apis/sending-larger-files).
- **Block type compatibility**: Files can be attached to image, file, video, audio, or pdf blocks — and to `files` properties on pages.
**What’s Next** Now that you know how to upload a file, let’s walk through how to retrieve a file via the API: