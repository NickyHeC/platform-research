This feature is currently in **beta**. The setup flow and capabilities may change.

This guide walks you through connecting [Cursor](https://cursor.com/) to a Notion custom agent. Once connected, your agent can turn a page, task, or comment into working code and a pull request — and it can keep running in the background while you move on to other work. With this integration, you can:
- **Create PRs from Notion** — Start a pull request from a page, task, or comment
- **Fix bugs from tasks** — Point the agent at a bug report and let it produce a fix
- **Run in the background** — Close the page and come back later to find a PR link waiting

## Prerequisites

Before you start, make sure you have:
- A [custom agent](https://www.notion.com/help/custom-agent) in your Notion workspace
- A [Cursor](https://cursor.com/) account (logging in with GitHub gives the easiest setup)
During setup, you’ll create a **Cursor User API Key** and paste it into Notion.

## Set up the connection

### 1\. Add the Cursor connection in Notion

### 2\. Create a User API Key in Cursor

### 3\. Finish the connection in Notion

Cursor is now connected and your agent can write code and open pull requests directly from your tasks or agent chat.

## Using the agent

There are two ways to hand work to your agent:
- **Assign a database page** (like a task) to the agent
- **@mention the agent** in a comment on a page or task
When you do, be direct about what you want it to build and where the work should land. For example:
- *“Create a PR from this spec in \[repo URL\]”*
- *“Start this in the background, then open a PR when it’s ready.”*
- *“Fix the bug described in this task and update the task.”*
![Assigning a task to the agent with a clear instruction](https://mintcdn.com/notion-demo/OSeEitqkonP_Uquz/images/docs/agents/assign-task.png?w=2500&fit=max&auto=format&n=OSeEitqkonP_Uquz&q=85&s=54b17e167f6abedc3b375e03885c3e52)

Assigning a task to the agent with a clear instruction

Your agent can keep working after you close the page or agent chat. To check on progress, open the agent and look at its chat activity for status updates and links.

## Troubleshooting

Progress lives in the agent’s **chat activity**, even if you started the work from a task comment. Open the agent to see status updates and PR links.

Use the agent’s **chat** when you want a single thread of status updates. Use **task comments** when you want the work to stay attached to a specific page.

Share the relevant pages and databases with the agent so it can read the spec, task, and any linked context. You can update shared pages in the agent’s **Settings** → **Tools & access**.

Give it a minute, then confirm:
- Cursor is connected (check **Settings** → **Tools & access**)
- Your API key is still valid
- The agent has access to the task and any referenced pages

Reconnect Cursor in **Tools & access** using a fresh API key. The old key is no longer valid after rotation.