"prelimitary tags cog, will be updated later"

from .basecog import BaseCog, Bot
from discord.app_commands import command as acommand
import discord


class Tags(BaseCog):
    @acommand()
    async def tag(self, ctx, tag_name: str):
        "Get a tag"
        tag = self.bot.tags.get(ctx.guild.id, tag_name)
        if tag:
            await ctx.send(tag[0], allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(f"Tag {tag_name} not found!")
