# discord-guild-mcp

A read-only [MCP](https://modelcontextprotocol.io) server that gives Claude access to a
Discord guild's structure: channels, roles, members, and recent message history.

It has no bot presence, no gateway connection, and no slash commands. It's a query layer:
Claude calls a tool, the server makes a REST call to Discord, Claude gets data back. It
never posts messages or modifies the guild.

## Tools

| Tool | Returns |
|------|---------|
| `get_guild_info()` | Guild name, description, member counts, feature flags |
| `list_channels()` | All channels grouped by category, with type and topic |
| `list_roles()` | All roles with name, color, position, mentionable flag |
| `list_members(limit=100)` | Up to `limit` members with username, roles, join date |
| `get_channel_messages(channel_id, limit=25)` | Recent messages from a channel |

## Prerequisites

You need an existing Discord bot application (this reuses the same bot as chikbot-py, or
you can register a new one at the
[Discord Developer Portal](https://discord.com/developers/applications)).

The bot must already be a member of the target server. Registering an application doesn't
add it to your server — that requires an OAuth2 invite, done once when the bot was
originally set up.

On that bot application, enable two privileged intents (**Bot** tab in the Developer
Portal):
- **Server Members Intent** — required for `list_members`
- **Message Content Intent** — required for `get_channel_messages`

You'll also need:
- The bot token (**Bot** tab → Reset/Copy Token)
- The guild ID (enable Developer Mode in Discord's User Settings → Advanced, then
  right-click the server icon → Copy Server ID)

## Setup

The server runs in Docker — Claude Code spawns a fresh container per session over stdio,
so there's no persistent process and no local Python environment to manage.

Build the image after cloning or after any code change:

```
cd discord-guild-mcp
docker build -t discord-guild-mcp .
```

Rebuilding is only needed when `config.py`, `discord_client.py`, `server.py`, or
`requirements.txt` change. Editing the guild ID or token doesn't require a rebuild — those
are runtime environment variables, not baked into the image.

### Manual local testing (optional)

To run the server directly and confirm it starts without going through Claude Code:

```
cp .env.example .env
# fill in DISCORD_BOT_TOKEN and DISCORD_GUILD_ID
docker compose run --rm mcp
```

## Registering with Claude Code

MCP servers are registered with the `claude mcp add` CLI, not by hand-editing
`settings.json`. Register the server at user scope so it's available in every project:

```
claude mcp add discord-guild -s user -e DISCORD_BOT_TOKEN=your_token_here -e DISCORD_GUILD_ID=your_guild_id_here -- docker run -i --rm -e DISCORD_BOT_TOKEN -e DISCORD_GUILD_ID discord-guild-mcp
```

The bare `-e KEY` flags (no `=value`) in the `docker run` command forward those variables
from the spawned process's environment — which Claude Code sets from the `env` block —
straight into the container.

Run `/mcp` inside Claude Code to confirm it shows as connected.

### Querying multiple guilds

Since the guild ID is just an environment variable, the same image can be registered
multiple times under different names to query different servers:

```
claude mcp add discord-guild-2 -s user -e DISCORD_BOT_TOKEN=your_token_here -e DISCORD_GUILD_ID=other_guild_id -- docker run -i --rm -e DISCORD_BOT_TOKEN -e DISCORD_GUILD_ID discord-guild-mcp
```

Claude will call tools from whichever server you reference by name (e.g. "use
discord-guild-2 to list channels").

## Project layout

```
server.py            FastMCP app; all tool definitions; entry point
discord_client.py     All Discord REST calls; thin async HTTP wrapper
config.py             Env loading with startup validation
Dockerfile             Image build for the server
docker-compose.yml     Local build/run convenience for manual testing
requirements.txt
.env.example
```
