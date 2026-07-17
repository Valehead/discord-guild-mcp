import httpx
from config import BOT_TOKEN, GUILD_ID

BASE = "https://discord.com/api/v10"
HEADERS = {"Authorization": f"Bot {BOT_TOKEN}"}


class DiscordClient:
    def __init__(self):
        self._client = httpx.AsyncClient(base_url=BASE, headers=HEADERS)

    async def get_guild(self) -> dict:
        r = await self._client.get(f"/guilds/{GUILD_ID}?with_counts=true")
        r.raise_for_status()
        return r.json()

    async def get_channels(self) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/channels")
        r.raise_for_status()
        return r.json()

    async def get_roles(self) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/roles")
        r.raise_for_status()
        return r.json()

    async def get_members(self, limit: int = 100) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/members?limit={limit}")
        r.raise_for_status()
        return r.json()

    async def get_messages(self, channel_id: str, limit: int = 25) -> list[dict]:
        r = await self._client.get(f"/channels/{channel_id}/messages?limit={limit}")
        r.raise_for_status()
        return r.json()

    async def get_active_threads(self) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/threads/active")
        r.raise_for_status()
        return r.json()["threads"]

    async def get_archived_threads(self, channel_id: str, limit: int = 50) -> list[dict]:
        r = await self._client.get(f"/channels/{channel_id}/threads/archived/public?limit={limit}")
        r.raise_for_status()
        return r.json()["threads"]

    async def get_channel(self, channel_id: str) -> dict:
        r = await self._client.get(f"/channels/{channel_id}")
        r.raise_for_status()
        return r.json()

    async def get_pins(self, channel_id: str) -> list[dict]:
        r = await self._client.get(f"/channels/{channel_id}/pins")
        r.raise_for_status()
        return r.json()

    async def search_members(self, query: str, limit: int = 25) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/members/search?query={query}&limit={limit}")
        r.raise_for_status()
        return r.json()

    async def get_member(self, user_id: str) -> dict:
        r = await self._client.get(f"/guilds/{GUILD_ID}/members/{user_id}")
        r.raise_for_status()
        return r.json()

    async def get_emojis(self) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/emojis")
        r.raise_for_status()
        return r.json()

    async def get_scheduled_events(self) -> list[dict]:
        r = await self._client.get(f"/guilds/{GUILD_ID}/scheduled-events?with_user_count=true")
        r.raise_for_status()
        return r.json()

    async def aclose(self):
        await self._client.aclose()
