from fastmcp import FastMCP
from discord_client import DiscordClient

mcp = FastMCP("discord-guild")
discord = DiscordClient()

CHANNEL_TYPES = {0: "text", 2: "voice", 4: "category", 5: "announcement",
                 13: "stage", 15: "forum", 16: "media"}


@mcp.tool()
async def get_guild_info() -> dict:
    """Returns the guild's name, description, approximate member count, and feature flags."""
    g = await discord.get_guild()
    return {
        "name": g["name"],
        "description": g.get("description"),
        "approximate_member_count": g.get("approximate_member_count"),
        "approximate_presence_count": g.get("approximate_presence_count"),
        "features": g.get("features", []),
        "verification_level": g["verification_level"],
        "id": g["id"],
    }


@mcp.tool()
async def list_channels() -> list[dict]:
    """Returns all channels grouped by category, with type, topic, and position."""
    channels = await discord.get_channels()
    categories = {c["id"]: c["name"] for c in channels if c["type"] == 4}
    return [
        {
            "id": c["id"],
            "name": c["name"],
            "type": CHANNEL_TYPES.get(c["type"], str(c["type"])),
            "category": categories.get(c.get("parent_id", ""), None),
            "topic": c.get("topic"),
            "position": c["position"],
            "nsfw": c.get("nsfw", False),
        }
        for c in sorted(channels, key=lambda x: (x.get("position", 0)))
        if c["type"] != 4
    ]


@mcp.tool()
async def list_roles() -> list[dict]:
    """Returns all roles with name, color (hex), position, and whether they're mentionable."""
    roles = await discord.get_roles()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "color": f"#{r['color']:06x}" if r["color"] else None,
            "position": r["position"],
            "mentionable": r["mentionable"],
            "hoist": r["hoist"],
            "managed": r["managed"],
        }
        for r in sorted(roles, key=lambda x: -x["position"])
    ]


@mcp.tool()
async def list_members(limit: int = 100) -> list[dict]:
    """Returns up to `limit` members (max 1000) with their username, display name, roles, and join date.
    Requires Server Members Intent enabled on the bot in the Discord Developer Portal."""
    members = await discord.get_members(min(limit, 1000))
    return [
        {
            "id": m["user"]["id"],
            "username": m["user"]["username"],
            "display_name": m.get("nick") or m["user"].get("global_name") or m["user"]["username"],
            "roles": m["roles"],
            "joined_at": m["joined_at"],
            "bot": m["user"].get("bot", False),
        }
        for m in members
    ]


@mcp.tool()
async def get_channel_messages(channel_id: str, limit: int = 25) -> list[dict]:
    """Returns the most recent `limit` messages from a channel (max 100).
    Use list_channels() to find channel IDs."""
    messages = await discord.get_messages(channel_id, min(limit, 100))
    return [
        {
            "id": m["id"],
            "author": m["author"]["username"],
            "content": m["content"],
            "timestamp": m["timestamp"],
            "edited_timestamp": m.get("edited_timestamp"),
            "attachments": [a["url"] for a in m.get("attachments", [])],
        }
        for m in messages
    ]


if __name__ == "__main__":
    mcp.run()
