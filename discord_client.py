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

    async def aclose(self):
        await self._client.aclose()
