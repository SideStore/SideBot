"Admin cog with commands for moderation"
from discord import Interaction, Member
from discord.app_commands import command, describe, checks, errors
from discord.ext.commands import Bot, Cog


class Admin(Cog):
    "Admin cog with commands for moderation"
    def __init__(self, bot: Bot):
        self.bot = bot
        self.description = "This is the moderation cog"

    @command(name="clean", description="Clean messages from channel")
    @describe(count="Amount of messages to delete")
    @describe(member="The member to delete the messages from")
    @checks.has_permissions(manage_messages=True)
    async def clean(self, inter: Interaction, count: int, member: Member | None = None):
        "Cleans `count` messages from optional `member` in the channel it's used"
        await inter.response.defer(ephemeral=True)
        if member:
            del_messages = []
            async for message in inter.channel.history(limit=200):
                if len(del_messages) >= count:
                    break
                if message.author == member:
                    del_messages.append(message)
            await inter.channel.delete_messages(del_messages)
        else:
            del_messages = await inter.channel.purge(limit=count)
        await inter.followup.send(f"Attempted to delete {count} messages,"
                                  f"actually deleted {len(del_messages)}!", ephemeral=True)

    @clean.error
    async def app_command_error(self, inter: Interaction, err: errors.AppCommandError):
        "Handle app command errors"
        if isinstance(err, errors.MissingPermissions):
            return await inter.response.send_message("You do not have permission to run this command.",
                                                     ephemeral=True)
        return await inter.response.send_message(f"{err}", ephemeral=True)

async def setup(bot: Bot):
    "Set up the cog for bot"
    await bot.add_cog(Admin(bot))
