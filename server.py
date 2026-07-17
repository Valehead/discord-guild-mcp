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
    """Returns all channels grouped by category, with type, topic, and position.
    Forum channels don't hold messages directly: use list_active_threads() or
    list_archived_threads() to find posts, not get_channel_messages() on the forum ID."""
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
    return [_shape_member(m) for m in members]


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


def _shape_thread(t: dict) -> dict:
    metadata = t.get("thread_metadata", {})
    return {
        "id": t["id"],
        "name": t["name"],
        "parent_id": t.get("parent_id"),
        "message_count": t.get("message_count"),
        "member_count": t.get("member_count"),
        "archived": metadata.get("archived"),
        "created_at": metadata.get("create_timestamp"),
        "owner_id": t.get("owner_id"),
    }


def _shape_member(m: dict) -> dict:
    return {
        "id": m["user"]["id"],
        "username": m["user"]["username"],
        "display_name": m.get("nick") or m["user"].get("global_name") or m["user"]["username"],
        "roles": m["roles"],
        "joined_at": m["joined_at"],
        "bot": m["user"].get("bot", False),
    }


@mcp.tool()
async def list_active_threads(channel_id: str | None = None) -> list[dict]:
    """Returns all active (non-archived) threads in the guild, including forum posts.
    Pass channel_id to filter to threads under one parent channel (e.g. a forum)."""
    threads = await discord.get_active_threads()
    if channel_id is not None:
        threads = [t for t in threads if t.get("parent_id") == channel_id]
    return [_shape_thread(t) for t in threads]


@mcp.tool()
async def list_archived_threads(channel_id: str, limit: int = 50) -> list[dict]:
    """Returns up to `limit` archived public threads under a channel (e.g. old forum
    posts), most recent first. Use list_channels() to find channel IDs."""
    threads = await discord.get_archived_threads(channel_id, min(limit, 100))
    return [_shape_thread(t) for t in threads]


@mcp.tool()
async def get_channel(channel_id: str) -> dict:
    """Returns detail for a single channel: common fields plus type-specific extras
    (forum tags/default reaction, or thread message/member counts and archive state)."""
    c = await discord.get_channel(channel_id)
    result = {
        "id": c["id"],
        "name": c["name"],
        "type": CHANNEL_TYPES.get(c["type"], str(c["type"])),
        "topic": c.get("topic"),
        "parent_id": c.get("parent_id"),
        "nsfw": c.get("nsfw", False),
    }
    if "available_tags" in c:
        result["available_tags"] = c["available_tags"]
    if "default_reaction_emoji" in c:
        result["default_reaction_emoji"] = c["default_reaction_emoji"]
    if "message_count" in c:
        result["message_count"] = c["message_count"]
    if "member_count" in c:
        result["member_count"] = c["member_count"]
    if "thread_metadata" in c:
        result["thread_metadata"] = c["thread_metadata"]
    return result


@mcp.tool()
async def get_pinned_messages(channel_id: str) -> list[dict]:
    """Returns all pinned messages in a channel."""
    messages = await discord.get_pins(channel_id)
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


@mcp.tool()
async def search_members(query: str, limit: int = 25) -> list[dict]:
    """Returns up to `limit` members (max 1000) whose username or nickname starts with
    `query`. Requires Server Members Intent, same as list_members()."""
    members = await discord.search_members(query, min(limit, 1000))
    return [_shape_member(m) for m in members]


@mcp.tool()
async def get_member(user_id: str) -> dict:
    """Returns a single member's username, display name, roles, and join date."""
    m = await discord.get_member(user_id)
    return _shape_member(m)


@mcp.tool()
async def list_emojis() -> list[dict]:
    """Returns the guild's custom emojis with name and animated/available flags."""
    emojis = await discord.get_emojis()
    return [
        {
            "id": e["id"],
            "name": e["name"],
            "animated": e.get("animated", False),
            "available": e.get("available", True),
        }
        for e in emojis
    ]


@mcp.tool()
async def list_scheduled_events() -> list[dict]:
    """Returns the guild's scheduled events with time, status, and interested user count."""
    events = await discord.get_scheduled_events()
    return [
        {
            "id": e["id"],
            "name": e["name"],
            "description": e.get("description"),
            "scheduled_start_time": e.get("scheduled_start_time"),
            "scheduled_end_time": e.get("scheduled_end_time"),
            "status": e["status"],
            "entity_type": e["entity_type"],
            "user_count": e.get("user_count"),
        }
        for e in events
    ]


if __name__ == "__main__":
    mcp.run()
