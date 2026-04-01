Now that you have installed the Notion MCP, let’s explore how AI assistants can use Notion MCP tools to create, search, and manage content in your Notion workspace. These tools work seamlessly together through prompts, and their real power comes from combining them. With a single prompt, you can search your workspace, create new pages from the results, and update properties across multiple pages. Understanding these building blocks helps you craft efficient prompts that tackle complex tasks by combining multiple tools.

## MCP tools

`notion-search` Search across your Notion workspace and connected tools like Slack, Google Drive, and Jira.

Requires Notion AI access. Without a Notion AI plan, search is limited to your Notion workspace only.

**Example prompts:**
- “Check Slack for how we solved this bug in the past”
- “Search for documents mentioning ‘budget approval process’”
- “Look for meeting notes from last week with John”
- “Find all project pages that mention ‘ready for dev’”

`notion-fetch` Retrieves content from a Notion page, database, or data source by its URL or ID. You can pass a data source ID (from `collection://...` tags in database responses) to fetch details about that specific data source, including its schema and properties. When fetching a database, the response includes available templates for each data source, which can be used with the create-pages and update-page tools.**Example prompts:**
- “What product requirements still need to be implemented from this ticket `https://notion.so/page-url`?”
- “Fetch the data source `collection://f336d0bc-b841-465b-8045-024475c079dd` to see its schema”
- “Fetch the bug tracking database so I can see the available templates”

`notion-create-pages` Creates one or more Notion pages with specified properties and content. Supports applying [database templates](https://developers.notion.com/guides/data-apis/creating-pages-from-templates) to pre-populate new pages with content and property values. Each page can optionally have an icon (emoji, custom emoji by name, or external URL) and a cover image. If a parent is not specified, a private page will be created.**Example prompts:**
- “Create a project kickoff page under our Projects folder with agenda and team info”
- “Make a new employee onboarding checklist in our HR database”
- “Create a new bug report in the tracking database using the ‘Urgent Bug’ template”
- “Add a new product feature request to our feature database”
- “Create a page with the 🚀 icon and a cover image”

`notion-update-page` Update a Notion page’s properties, content, icon, or cover. Supports applying [database templates](https://developers.notion.com/guides/data-apis/creating-pages-from-templates) to existing pages. Icon and cover can be set alongside any update command.**Example prompts:**
- “Change the status of this task from ‘In Progress’ to ‘Complete’”
- “Add a new section about risks to the project plan page”
- “Apply the project kickoff template to this page”
- “Set the page icon to 🎯 and add a cover image”
- “Remove the icon from this page”

`notion-move-pages` Move one or more Notion pages or databases to a new parent.**Example prompts:**
- “Move my weekly meeting notes page to the ‘Team Meetings’ page”
- “Reorganize all project documents under the ‘Active Projects’ section”

`notion-duplicate-page` Duplicate a Notion page within your workspace. This action completes asynchronously.**Example prompts:**
- “Duplicate my project template page so I can use it for the new Q3 initiative”
- “Make a copy of the meeting agenda template for next week’s planning session”

`notion-create-database` Creates a new Notion database, initial data source, and initial view with the specified properties.**Example prompts:**
- “Create a new database to track our customer feedback with fields for customer name, feedback type, priority, and status”
- “Set up a content calendar database with columns for publish date, content type, and approval status”

`notion-update-data-source` Update a Notion data source’s properties, name, description, or other attributes.**Example prompts:**
- “Add a status field to track project completion”
- “Update the task database to include priority levels”

`notion-create-view` Create a new view on a Notion database. Supports table, board, list, calendar, timeline, gallery, form, chart, map, and dashboard view types. Use the optional configuration DSL for filters, sorts, grouping, and display options.**Example prompts:**
- “Create a board view grouped by Status in my tasks database”
- “Add a calendar view to the project tracker that shows items by due date”
- “Set up a filtered table view that only shows in-progress items, sorted by priority”
- “Create a timeline view for the roadmap database using start and end dates”
- “Create a chart view showing task counts by status as a bar chart”
- “Add a form view to the feedback database for collecting responses”
- “Create a map view of office locations using the Address property”

`notion-update-view` Update a view’s name, filters, sorts, or display configuration. Only the fields you specify will be changed. Supports clearing existing configuration like filters, sorts, and grouping.**Example prompts:**
- “Rename the ‘All Tasks’ view to ‘Sprint Board’”
- “Update the board view to filter by status equals ‘Done’”
- “Clear the filters on this view and add a sort by created date”
- “Change the view to group by priority and only show Name and Status columns”

`notion-query-data-sources` Query across multiple Notion data sources directly with structured summaries, grouping, and filters. Returns organized results with counts and rollups for quick scanning.

Requires Enterprise plan with Notion AI.

**Example prompts:**
- “What’s due for me this week across all tasks and meeting note action items? Group by priority.”
- “Show all risks from Engineering and Product databases this month, grouped by owner.”

`notion-query-database-view` Query data from a Notion database using a pre-defined [view’s filters and sorts](https://www.notion.com/help/views-filters-and-sorts).

Requires Business plan or higher with Notion AI. Only available when the `notion-query-data-sources` tool is not available.

**Example prompts:**
- “Query my ‘In Progress’ tasks view to see what I’m currently working on”
- “Get all items from the ‘High Priority’ view in our feature requests database”
- “Export the filtered data from the ‘Q1 Goals’ view for analysis”

`notion-get-teams` Retrieves a list of teams (teamspaces) in the current workspace.**Example prompts:**
- “Search for teams by name, and your membership status in each team”
- “Get a team’s ID to use as a filter for a search”

`notion-get-users` Lists all users in the workspace with their details.**Example prompts:**
- “Get contact details for the user who created this page”
- “Look up the profile of the person assigned to this task”

`notion-get-user` Retrieve your user information by ID.**Example prompts:**
- “What’s my email address?”
- “What’s my Notion user ID?”

`notion-get-self` Retrieves information about your own bot user and the Notion workspace you’re connected to.**Example prompts:**
- “Which Notion workspace am I currently connected to?”
- “What’s my file size upload limit for the current workspace?”

**Tool names may vary for OpenAI** When connecting with an OpenAI MCP client (e.g. ChatGPT), the `notion-` prefix is automatically omitted from the `notion-fetch` and `notion-search` tools, making them appear as `fetch` and `search`, respectively. This is because these specific tool names are required as part of the [Deep Research specification](https://platform.openai.com/docs/guides/deep-research#remote-mcp-servers) for remote MCP servers.

## Rate limits

Standard [API request limits](https://developers.notion.com/reference/request-limits) apply per user’s usage of Notion MCP (totaled across all tool calls). Currently, this is an average of **180 requests per minute** (3 requests per second). Some MCP tools have additional, tool-specific rate limits that are stricter. These are subject to change over time, but the current values are listed below for reference:
- **Search**: 30 requests per minute

### Examples

To illustrate the above limitations, you’ll experience rate limit errors in your MCP client of choice in any of the following example scenarios (assuming we take the average rate over a large enough time window):
- 35 searches per minute (exceeds search-specific limit)
- 12 searches & 170 fetches per minute (exceeds general 180 requests/min limit)
- 185 fetches per minute (exceeds general 180 requests/min limit)

### What to do if you’re rate-limited

In most cases, the time it takes to do a complex AI-powered search across Notion and your connected tools means that sequential searches will typically stay under the rate limit. In general, if you encounter rate limit errors, prompt your LLM tool to reduce the amount of parallel searches or operations performed using Notion MCP, and/or try again later.