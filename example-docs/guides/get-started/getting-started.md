## Using Notion’s public API for integrations

A Notion workspace is a collaborative environment where teams can organize work, manage projects, and store information in a highly customizable way. Notion’s REST API facilitates direct interactions with workspace elements through programming. Key functionalities include: To make interactions within Notion workspaces programmatically, you must associate these actions with a Notion user. Notion facilitates this by allowing API requests to be linked to a “bot” user. Developers create integrations to define a bot’s capabilities, including authenticating API requests, deciding when to make requests, and setting the bot’s read/write permissions. Essentially, using Notion’s Public API involves creating an integration that outlines how a bot interacts with your workspace and assigns REST API requests to the bot. There are two primary integration types:
- [**Internal**](#internal-vs-public-integrations): For private workspace workflows and automations.
- [**Public**](#internal-vs-public-integrations): For broader, shareable functionalities, including [Link Previews](https://developers.notion.com/guides/link-previews/link-previews).
For further details on integration possibilities and API specifics, proceed with the guide or consult the [API reference](https://developers.notion.com/reference/intro). Check out our [demos](https://developers.notion.com/page/examples) for practical examples.

## What is a Notion integration?

A Notion integration, sometimes referred as a [connection](https://www.notion.so/help/add-and-manage-connections-with-the-api), enables developers to programmatically interact with Notion workspaces. These integrations facilitate linking Notion workspace data with other applications or the automation of workflows within Notion. Integrations are installed in Notion workspaces and require **explicit permission** from users to access Notion pages and databases. ![](https://mintcdn.com/notion-demo/LHm9qfrJYJOPRxs6/images/docs/0f06356-notion_overview.jpg?w=2500&fit=max&auto=format&n=LHm9qfrJYJOPRxs6&q=85&s=c06a22ed64ca97f2a5cd442c5edbefc8) Notion users have access to a vast [library](https://www.notion.so/integrations/all) of existing integrations to enrich their experience further. For developers interested in creating custom solutions, Notion supports the development of both internal and public integrations. Both utilize the Notion API for workspace interactions. Let’s explore internal and public integrations.

## Internal vs. public integrations

Notion integrations come in two types: Internal and Public. Understanding the differences between them helps in choosing the right approach for your development needs.
- **Internal Integrations** are exclusive to a single workspace, accessible only to its members. They are ideal for custom workspace automations and workflows.
- **Public Integrations** are designed for a wider audience, usable across any Notion workspace. They cater to broad use cases and follow the OAuth 2.0 protocol for workspace access.

Public integrations must undergo a Notion security review before publishing.

### Key differences

| Feature | Internal Integrations | Public Integrations |
| --- | --- | --- |
| Scope | Confined to a single, specific workspace. | Available across multiple, unrelated workspaces. |
| User Access | Only accessible by members of the workspace where it’s installed. | Accessible by any Notion user, regardless of their workspace. |
| Creation | Created by Workspace Owners within the integration dashboard. | Created by Workspace Owners within the integration dashboard. |
| Permissions | Workspace members explicitly grant access to their pages or databases via Notion’s UI. | Users authorize access to their pages during the OAuth flow, or by sharing pages directly with the integration. |
| OAuth Protocol | Not applicable, as access is limited to a single workspace. | Uses the OAuth 2.0 protocol to securely access information across multiple workspaces. |
| Dashboard Visibility | Visible to Workspace Owners in the integration dashboard, including integrations created by others. | \- |

## What you can build

Notion’s REST API opens up a world of possibilities for integrations, ranging from enhancing internal workflow to creating public-facing applications. Here’s a closer look at some of the innovative integrations developers have built with Notion:

### Data integrations

Data integrations leverage the Notion API to automate data flow between Notion and other systems.
- **Automated Notifications:** Develop integrations that monitor Notion databases for changes. Upon detecting a change, these integrations can automatically send notifications various communication channels.
- **Github Synchronization**: Create integrations that keep Notion issues in sync with GitHub issues.
- **External Data Import:** Build integrations that import data from external sources directly into Notion databases. This can include importing customer data, project updates, or any other relevant information.

## Examples:

## Create an integration

## Working with databases

## Working with files and media

## Working with page content

### Link preview integrations

Enhance the sharing experience within Notion with Link preview integrations, offering a glimpse into the content of shared links: ![](https://mintcdn.com/notion-demo/LHm9qfrJYJOPRxs6/images/docs/ce5daa3-Screen_Shot_2023-06-27_at_3.48.22_PM.png?w=2500&fit=max&auto=format&n=LHm9qfrJYJOPRxs6&q=85&s=b25033a6958a4ed0623146ab6e5cd512) Create integrations that allow for the customization of how shared links are presented in Notion, providing context and enhancing engagement.

Link Preview Integrations differ from public integrations. Review the [Link Preview guide](https://developers.notion.com/guides/link-previews/build-a-link-preview-integration).

To build a Link Preview integration, developers must first apply for access to the feature through the [Notion Link Preview API request form](https://notionup.typeform.com/to/BXheLK4Z?typeform-source=developers.notion.com).Link Preview integrations published for distribution require a review from Notion’s platform and security teams.

## Quick Links

## Introduction to Link Preview integrations

## Build a Link Preview integration

## API reference docs for the Link Preview unfurl attribute object

## Help Centre

### Identity management integrations (Enterprise only)

For enterprise-level workspaces, Notion offers advanced identity management capabilities:
- **SCIM API for User and Group Management**: Utilize the SCIM API to automate the provisioning and management of users and groups within enterprise workspaces, streamlining administrative tasks.
- **SAML SSO for Enhanced Security**: Implement Single Sign-On (SSO) using SAML for a secure and convenient authentication process, simplifying access for users across the enterprise.

## Quick Links

## Provision users and groups with SCIM

## SAML SSO configuration

## Starting your integration journey

Embarking on building an integration with Notion? Begin with our foundational [*Build your first integration guide*](https://developers.notion.com/guides/get-started/create-a-notion-integration). As you become more familiar with the basics, expand your knowledge and skills with in-depth guides on [Authorization](https://developers.notion.com/guides/get-started/authorization), [Page content](https://developers.notion.com/guides/data-apis/working-with-page-content), and [Databases](https://developers.notion.com/guides/data-apis/working-with-databases).

## Key resources

- [Notion SDK for JavaScript](https://github.com/makenotion/notion-sdk-js): Leverage our SDK designed for JavaScript environments to simplify interactions with the REST API, making development more efficient.
- [Technology Partner Program](https://www.notion.so/technology-partner-program): Have you developed a public integrations? Join our Technology Partner Program for access to dedicated support, exclusive distribution channels, and marketing opportunities.
Explore these resources and join the [Notion Devs Slack community](https://join.slack.com/t/notiondevs/shared_invite/zt-3u9oid9q8-HLUBmMVWYK~g9HFo4U4raA) to share your projects, gain insights from fellow developers, and discover new ways to enhance Notion with integrations.