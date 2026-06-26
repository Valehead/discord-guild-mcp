import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID: str  = os.environ["DISCORD_GUILD_ID"]
