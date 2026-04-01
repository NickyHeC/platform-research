Files, images, and other media bring your Notion workspace to life — from company logos and product photos to contract PDFs and design assets. With the Notion API, you can programmatically upload, attach, and reuse these files wherever they’re needed. In this guide, you’ll learn how to:
- Upload a new file using the **Direct Upload** method (single-part)
- Retrieve existing files already uploaded to your workspace
We’ll also walk through the different upload methods and supported file types, so you can choose the best path for your integration.

## Upload methods at a glance

The Notion API supports three ways to add files to your workspace:

| Upload method | Description | Best for |
| --- | --- | --- |
| [**Direct Upload**](https://developers.notion.com/guides/data-apis/uploading-small-files) | Upload a file (≤ 20MB) via a `multipart/form-data` request | The simplest method for most files |
| [**Direct Upload (multi-part)**](https://developers.notion.com/guides/data-apis/sending-larger-files) | Upload large files (> 20MB) in chunks across multiple requests | Larger media assets and uploads over time |
| [**Indirect Import**](https://developers.notion.com/guides/data-apis/importing-external-files) | Import a file from a publicly accessible URL | Migration workflows and hosted content |

## Supported block types

Uploaded files can be attached to:
- Media blocks: `file`, `image`, `pdf`, `audio`, `video`
- Page properties: `files` properties in databases
- Page-level visuals: page `icon` and `cover`

**Need support for another block or content type**? Let us know [here](https://notiondevs.notion.site/1f8a4445d271805da593dd86bd86872b?pvs=105).

## Supported file types

Before uploading, make sure your file type is supported. Here’s what the API accepts:

| Category | Extensions | MIME types |
| --- | --- | --- |
| **Audio** | .aac,.adts,.mid,.midi,.mp3,.mpga,.m4a,.m4b,.mp4,.oga,.ogg,.opus,.wav,.wma,.weba,.flac | audio/aac, audio/midi, audio/mpeg, audio/mp4, audio/ogg, audio/wav, audio/x-ms-wma, audio/webm, audio/x-flac |
| **Document** | .pdf,.txt,.csv,.json,.doc,.dot,.docx,.dotx,.xls,.xlt,.xla,.xlsx,.xltx,.ppt,.pot,.pps,.ppa,.pptx,.potx,.rtf,.md,.markdown,.html,.htm,.epub,.xml,.css,.odt,.ods,.odp,.ics,.yaml,.yml,.tsv,.zip,.gz,.gzip,.tar,.7z,.bz2,.rar | application/pdf, text/plain, text/csv, application/json, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.openxmlformats-officedocument.wordprocessingml.template, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.openxmlformats-officedocument.spreadsheetml.template, application/vnd.ms-powerpoint, application/vnd.openxmlformats-officedocument.presentationml.presentation, application/vnd.openxmlformats-officedocument.presentationml.template, application/rtf, text/markdown, text/html, application/epub+zip, text/xml, application/xml, text/css, application/vnd.oasis.opendocument.text, application/vnd.oasis.opendocument.spreadsheet, application/vnd.oasis.opendocument.presentation, text/calendar, text/yaml, text/tab-separated-values, application/zip, application/gzip, application/x-tar, application/x-7z-compressed, application/x-bzip2, application/vnd.rar |
| **Image** | .gif,.heic,.jpeg,.jpg,.png,.svg,.tif,.tiff,.webp,.ico,.bmp,.avif,.apng | image/gif, image/heic, image/jpeg, image/png, image/svg+xml, image/tiff, image/webp, image/vnd.microsoft.icon, image/bmp, image/avif, image/apng |
| **Video** | .amv,.asf,.wmv,.avi,.f4v,.flv,.gifv,.m4v,.mp4,.mkv,.webm,.mov,.qt,.mpeg,.ogv,.3gp,.3g2 | video/x-amv, video/x-ms-asf, video/x-msvideo, video/x-f4v, video/x-flv, video/mp4, application/mp4, video/webm, video/quicktime, video/mpeg, video/ogg, video/3gpp, video/3gpp2 |

**Ensure your file type matches the context** For example:
- You can’t use a video in an image block
- Page icons can’t be PDFs
- Text files can’t be embedded in video blocks

### File size limits

- **Free** workspaces are limited to **5 MiB (binary megabytes) per file**
- **Paid** workspaces are limited to **5 GiB per file**.
	- Files larger than 20 MiB must be split into parts and [uploaded using multi-part mode](https://developers.notion.com/guides/data-apis/sending-larger-files) in the API.
These are the same [size limits that apply](https://www.notion.com/pricing) to uploads in the Notion app UI. Use the [Retrieve a user](https://developers.notion.com/reference/get-user) or [List all users](https://developers.notion.com/reference/get-users) API to get the file size limit for a [bot user](https://developers.notion.com/reference/user#bots). Public integrations that can be added to both free or paid workspaces can retrieve or cache each bot’s file size limit. This can help avoid HTTP 400 validation errors for attempting to [send](https://developers.notion.com/reference/upload-file) files above the size limit.

```typescript
type APIUserObject = {
  object: "user",
  type: "bot",
  // ... other fields omitted

  bot: {
    // ... other fields omitted

    // Limits and restrictions that apply to the bot's workspace.
    workspace_limits: {
      // The maximum allowable size of a file upload, in bytes.
      max_file_upload_size_in_bytes: number,
    },
  }
}
```

For example, in a free workspace where bots are limited to FileUploads of 5 MiB, the response looks like:

```json
{
  "object": "user",
  "id": "be51669b-1932-4a11-8d35-38fbc2e1e4fd",
  "type": "bot",
  "bot": {
    "owner": {
      "type": "workspace"
    },
    "workspace_name": "Cat's Notion",
    "workspace_limits": {
      "max_file_upload_size_in_bytes": 5242880
    }
  }
}
```

### Other limitations

The rest of the pages in this guide, as well as the API reference for the File Upload API, include additional validations and restrictions to keep in mind as you build your integration and send files. One final limit to note here is both the [Create a file upload](https://developers.notion.com/reference/create-file) and [Send a file upload](https://developers.notion.com/reference/upload-file) APIs allow a maximum length of a `filename` (including the extension) of 900 bytes. However, we recommend using shorter names for performance and easier file management and lookup using the [List file uploads](https://developers.notion.com/reference/list-file-uploads) API. **What’s Next** Now that you know what’s supported, let’s walk through a real upload using the simplest method: uploading a single file in one request.