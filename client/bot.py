import typing as t

import aiohttp
import discord
from discord.ext import commands
from loguru import logger

from client.config import Config

EXTENSIONS = ["client.extensions." + ext for ext in ["user_watcher"]]


class Bot(commands.Bot):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.http_session: aiohttp.ClientSession = None

    async def login(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.http_session = aiohttp.ClientSession()
        await super().login(*args, **kwargs)

        logger.info(f"Logged in as {self.user}")

    async def setup_hook(self) -> None:
        await self.load_all_extensions()
        await super().setup_hook()

    async def close(self) -> None:
        await self.unload_all_extensions()

        await super().close()
        await self.http_session.close()
        await logger.complete()

    async def unload_all_extensions(self) -> None:
        logger.info("Unloading all extensions...")
        for extension in EXTENSIONS:
            await self.unload_extension(extension)

        logger.info("All extensions unloaded")

    async def load_all_extensions(self) -> None:
        logger.info("Loading all extensions...")
        for extension in EXTENSIONS:
            await self.load_extension(extension)

        logger.info("All extensions loaded")


_intents = discord.Intents(
    members=True,
)
_activity = discord.Activity(type=discord.ActivityType.watching, name="out for user updates!")
_allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)

BOT = Bot(
    command_prefix=Config.BOT_PREFIX,
    intents=_intents,
    allowed_mentions=_allowed_mentions,
    activity=_activity,
    case_insensitive=True,
)
