"""Admin cog with commands for moderation."""

import asyncio
from datetime import timedelta

import discord
from discord import Interaction, Member, Message, TextChannel
from discord.app_commands import command, default_permissions, describe, errors
from discord.ext import tasks
from discord.ext.commands import Bot

from .basecog import BaseCog


class SpamMessage:
    """A message representation."""

    __slots__ = ("i",)

    def __init__(self, i: int) -> None:
        """Initialize the message with the id."""
        self.i = i

    def __repr__(self) -> str:
        """Return the message representation."""
        return f"SpamMessage(i={self.i})"


class SpamChannel:
    """A channel representation that holds messages."""

    __slots__ = ("i", "messages")

    def __init__(self, i: int, messages: list[SpamMessage]) -> None:
        """Initialize the channel with the id and messages."""
        self.i = i
        self.messages = messages

    def __repr__(self) -> str:
        """Return the channel representation."""
        return f"SpamChannel(i={self.i}, messages={len(self.messages)})"

    def get_message(self, i: int) -> SpamMessage | None:
        """Get the message given the id, otherwise returns None."""
        m = [m for m in self.messages if m.i == i]
        return None if len(m) == 0 else m[0]


class SpamUser:
    """A user representation that holds channels."""

    __slots__ = ("i", "channels")

    def __init__(self, i: int, channels: list[SpamChannel]) -> None:
        """Initialize the user with the id and channels."""
        self.i = i
        self.channels = channels

    def __repr__(self) -> str:
        """Return the user representation."""
        return f"SpamUser(i={self.i}, channels={len(self.channels)})"

    def get_channel(self, i: int) -> SpamChannel | None:
        """Get the channel given the id, otherwise returns None."""
        c = [c for c in self.channels if c.i == i]
        return None if len(c) == 0 else c[0]


class Admin(BaseCog):
    """Admin cog with commands for moderation."""

    def __init__(self, bot: Bot, channels_max: int = 4) -> None:
        """Initialize the cog with the bot and the maximum channels to check."""
        self.spammers: list[SpamUser] = []
        self.clear_spammers.start()  # pylint: disable=E1101
        self.description = "This is the moderation cog"
        self.channels_max = channels_max
        super().__init__(bot)

    @command(name="clean", description="Clean messages from channel")
    @describe(count="Amount of messages to delete")
    @describe(member="The member to delete the messages from")
    @default_permissions(manage_messages=True)
    async def clean(
        self, inter: Interaction, count: int, member: Member | None = None
    ) -> None:
        """Clean `count` messages from optional `member` in the channel it's used."""
        if not isinstance(inter.channel, TextChannel):
            return await inter.response.send_message(
                "Not a text channel, doing nothing.",
                ephemeral=True,
            )
        await inter.response.defer(ephemeral=True)
        if member:
            del_messages: list[Message] = []
            async for message in inter.channel.history(limit=200):
                if len(del_messages) >= count:
                    break
                if message.author == member:
                    del_messages.append(message)
            await inter.channel.delete_messages(del_messages)
        else:
            del_messages = await inter.channel.purge(limit=count)
        await inter.followup.send(
            f"Attempted to delete {count} messages, actually deleted {len(del_messages)}!",
            ephemeral=True,
        )
        return None

    @clean.error
    async def app_command_error(
        self, inter: Interaction, err: errors.AppCommandError
    ) -> None:
        """Handle app command errors."""
        if isinstance(err, errors.MissingPermissions):
            return await inter.response.send_message(
                "You do not have permission to run this command.",
                ephemeral=True,
            )
        return await inter.response.send_message(f"{err}", ephemeral=True)

    @tasks.loop(minutes=30)
    async def clear_spammers(self) -> None:
        """Clear the current 'spammer' list."""
        self.logger.debug(self.spammers)
        self.spammers = []
        self.logger.debug("Cleared spammers")

    @BaseCog.listener()
    async def on_message(self, message: Message) -> None:
        """Handle messages to detect for spam."""
        if (
            self.bot.user is None
            or message.guild is None
            or message.author.id == self.bot.user.id
        ):
            return
        if message.author.id not in [su.i for su in self.spammers]:
            self.spammers.append(
                SpamUser(
                    message.author.id,
                    [
                        SpamChannel(
                            message.channel.id, [SpamMessage(message.id)]
                        )
                    ],
                ),
            )
            return
        cur = next(su for su in self.spammers if su.i == message.author.id)
        curch = cur.get_channel(message.channel.id)
        if curch:
            curch.messages.append(SpamMessage(message.id))
        else:
            cur.channels.append(
                SpamChannel(message.channel.id, [SpamMessage(message.id)]),
            )

        if len(cur.channels) >= self.channels_max:
            self.logger.info(
                "Spammer alert! %s has sent messages to %s different channels recently!",
                message.author.name,
                len(cur.channels),
            )
            if not isinstance(message.author, discord.User):
                await message.author.timeout(
                    timedelta(seconds=30),
                    reason=f"For spamming {len(cur.channels)} channels",
                )
            del_chans = []
            for channel in cur.channels:
                chan = self.bot.get_channel(channel.i)
                if isinstance(chan, TextChannel):
                    del_chans.append(
                        chan.delete_messages(
                            [
                                chan.get_partial_message(msg.i)
                                for msg in channel.messages
                            ],
                        ),
                    )
            await asyncio.gather(*del_chans)
            # await message.channel.send(f"Spammer alert! {message.author.name}
            # has sent messages to {len(cur)} different channels recently!", delete_after=5)
            self.spammers.pop(self.spammers.index(cur))
        self.logger.debug(self.spammers)


setup = Admin.setup
