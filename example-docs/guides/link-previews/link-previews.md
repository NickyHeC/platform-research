A Link Preview is a real-time excerpt of authenticated content that unfurls in Notion when an authenticated user shares an enabled link. Instead of logging in to multiple tools at a time, collaborators can use Link Previews to centralize their work in Notion. <video controls="" src="https://mintcdn.com/notion-demo/gQdVRy6l7aPTpzMm/images/docs/link_unfurling.mp4?fit=max&amp;auto=format&amp;n=gQdVRy6l7aPTpzMm&amp;q=85&amp;s=fb32ddf0c1c56950202668cb06b25b45"></video>With the Link Previews API, you can set up integrations that share a Link Preview for your product. For example:
- **Trello** created a Link Preview that unfurls information about a linked task.
- **Figma** built a Link Preview that shares a linked board’s image preview and corresponding metadata.
- **Amplitude** created a Link Preview that shares a linked graph in an iFrame along with an interface to modify the graph.
- **Slack** built a Link Preview that unfurls a linked message’s content and author.
If your customers use Notion, then building a Link Preview can help them to integrate your product into their existing workflows.

## How Link Previews work

A user shares a Link Preview enabled URL. Notion detects enabled URLs based on the settings that you provide when you create the integration. If it’s the first time that a user has shared an enabled URL, then Notion kicks off an auth flow to authenticate with your service. After the user authenticates, Notion and your service exchange tokens that enable your integration to share a Link Preview in the user’s workspace. ![](https://mintcdn.com/notion-demo/LHm9qfrJYJOPRxs6/images/docs/e121163-lp_overview.png?w=2500&fit=max&auto=format&n=LHm9qfrJYJOPRxs6&q=85&s=fa37c69b590afdcb471f43d6fd236352) Your integration also detects any changes to the data embedded in the Link Preview, and alerts Notion when the Link Preview needs to be updated. Notion alerts your integration when a Link Preview is deleted, so that your integration can stop listening for updates.

## Build your own Link Preview integration

Notion offers the tools for developers to build their own Link Preview integration to unfurl links for a specified domain. ![](https://mintcdn.com/notion-demo/LHm9qfrJYJOPRxs6/images/docs/57f4b0d-Untitled_1.png?w=2500&fit=max&auto=format&n=LHm9qfrJYJOPRxs6&q=85&s=8ebbf0df3e9aabec5e6ed794a9127c9c) Using the [Integration dashboard](https://www.notion.so/profile/integrations) and Notion’s public API, developers can customize each section of a Link Preview to show relevant data to users.

### Link Previews vs. Embed blocks

If you have used [Embed blocks](https://developers.notion.com/reference/block#embed) in Notion’s UI before, you may be wondering how Link Previews differ from them. Embeds allow Notion users to embed online content — such as a webpage, PDF, and more — directly in a Notion page. This allows users to preview the content without leaving Notion. Link Previews are similar but specifically allow developers to determine and customize the content displayed when an authenticated link is unfurled. Rather than embedding the full content of a webpage or file being shared, Link Previews pull data from a linked page and display it in an unfurled format that has been specified by the developer. Since Link preview integrations require [OAuth 2.0](https://www.oauth.com/) authentication, unfurled link content will update as the data being shared updates. For example, if a GitHub pull request is shared as a Link Preview, the data displayed in the preview will update as the pull request updates (e.g. when it is merged).

To learn more about Embed blocks, read our [reference docs](https://developers.notion.com/reference/block#embed) and [Help Centre guide](https://www.notion.so/help/embed-and-connect-other-apps).

## Requirements for building a Link Preview integration

To build a Link Preview integration, developers must first apply for access to the feature through the [Notion Link Preview API request form](https://notionup.typeform.com/to/BXheLK4Z?typeform-source=developers.notion.com).Additionally, all Link Preview integrations published for distribution require a review from Notion’s platform and security teams.

In order to build Link Preview integrations, you need to meet the following requirements:
- Support OAuth 2.0 in your application, or be ready to implement it.
- Own the domain that you’d like to set up with Link Preview enabled URLs.