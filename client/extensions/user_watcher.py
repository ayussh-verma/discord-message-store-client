import discord
import asyncio
from discord.ext import commands
from loguru import logger

from client.bot import Bot
from client.config import Config


class MemberWatcher(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.sync_completed = asyncio.Event()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        await self.sync_completed.wait()

        url = f"{Config.API_BASE_URL}/users/{after.id}"
        request_body = {
            "name": after.name,
            "avatarHash": getattr(after.avatar, "key", None),
            "guildAvatarHash": getattr(after.guild_avatar, "key", None),
            "joinedAt": after.joined_at.isoformat() if after.joined_at else None,
            "createdAt": after.created_at.isoformat(),
            "bot": after.bot,
            "inGuild": True,
        }

        response = await self.bot.http_session.get(url)
        if response.status == 200:
            await self.bot.http_session.put(url, json=request_body)
            return

        self.bot.http_session.post(url, json=request_body)

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        await self.sync_completed.wait()

        url = f"{Config.API_BASE_URL}/users/{payload.user.id}"
        request_body = {
            "inGuild": False,
            "name": payload.user.name,
            "avatarHash": getattr(payload.user.avatar, "key", None),
            "guildAvatarHash": None,
            "joinedAt": None,
            "createdAt": payload.user.created_at.isoformat(),
            "bot": payload.user.bot,
        }

        response = await self.bot.http_session.get(url)

        if response.status == 200:
            await self.bot.http_session.put(url, json=request_body)
            return

        self.bot.http_session.post(url, json=request_body)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.sync_completed.wait()

        url = f"{Config.API_BASE_URL}/users/{member.id}"
        request_body = {
            "name": member.name,
            "avatarHash": getattr(member.avatar, "key", None),
            "guildAvatarHash": getattr(member.guild_avatar, "key", None),
            "joinedAt": member.joined_at.isoformat() if member.joined_at else None,
            "createdAt": member.created_at.isoformat(),
            "bot": member.bot,
            "inGuild": True,
        }

        response = await self.bot.http_session.get(url, raise_for_status=True)

        if response.status == 200:
            await self.bot.http_session.put(url, json=request_body, raise_for_status=True)
            return

        self.bot.http_session.post(url, json=request_body, raise_for_status=True)

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild) -> None:
        if guild.id != Config.BOT_GUILD_ID:
            logger.info(f"Guild {guild.name} is not the target guild, discarding event.")
            return

        logger.info("Beginning member sync.")

        for member in guild.members:
            url = f"{Config.API_BASE_URL}/users/{member.id}"
            request_body = {
                "name": member.name,
                "avatarHash": getattr(member.avatar, "key", None),
                "guildAvatarHash": getattr(member.guild_avatar, "key", None),
                "joinedAt": member.joined_at.isoformat() if member.joined_at else None,
                "createdAt": member.created_at.isoformat(),
                "bot": member.bot,
                "inGuild": True,
            }

            response = await self.bot.http_session.get(url, raise_for_status=True)

            if response.status == 200:
                await self.bot.http_session.put(url, json=request_body, raise_for_status=True)
                continue

            self.bot.http_session.post(url, json=request_body, raise_for_status=True)

        self.sync_completed.set()

    async def cog_load(self) -> None:
        logger.info("Marking all members as having left the guild (inGuild=false)")

        stored_user_data_response = await self.bot.http_session.get(f"{Config.API_BASE_URL}/users")
        stored_user_data = await stored_user_data_response.json()

        for user in stored_user_data:
            await self.bot.http_session.put(
                f"{Config.API_BASE_URL}/users/{user['id']}", json=user | {"inGuild": False}, raise_for_status=True
            )

    def cog_unload(self) -> None:
        self.sync_completed.clear()


async def setup(bot: Bot) -> None:
    await bot.add_cog(MemberWatcher(bot))
