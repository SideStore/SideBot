"""The utility cog with various utility commands, listeners, etc."""

import random as randomorg

import discord
from discord import Interaction
from discord.app_commands import command
from discord.ext.commands import Bot, Cog


class Utility(Cog):
    """The utility cog with various utility commands, listeners, etc."""

    def __init__(
        self,
        bot: Bot,
        ultra_rare_threshold: float = 0.05,
        rare_threshold: float = 0.4,
    ) -> None:
        """Initialize the Utility cog."""
        self.bot = bot
        self.rare_threshold = rare_threshold
        self.ultra_rare_threshold = ultra_rare_threshold
        super().__init__()

    @command(name="status", description="Get how the bot is currently feeling")
    async def status(self, inter: Interaction) -> None:
        """Return the current bot status with quirky status messages."""
        ultra_rare_descriptions = [
            "84 is 48 backwards, and 84 is ny's favorite number! What is yours {name}?",
            "There are secrets beyond your comprehension {name} for you to find, but I am doing fine.",
            "{name}, I hope you've told those you hold dear that you love them today, I am doing fine.",
            "I would rate SideStore a solid Four Out Of Five, a great song, go listen to it {name}!",
        ]
        rare_descriptions = [
            "Hello {name}, I am doing fine, I promise.",
            "Snoozing.. Just kidding, hello {name}!",
            "{name}, have you heard the tale of secret_tunnel? Unlike that project, I am doing fine!",
        ]
        descriptions = [
            "Online!",
            "Doing Just Fine",
            "Why're you asking how a bot feels?",
            "If you're getting this message, just fine :)",
        ]
        random: randomorg.SystemRandom = randomorg.SystemRandom()
        rng = random.random()
        if rng < self.ultra_rare_threshold:
            description_pool = ultra_rare_descriptions
        elif rng < self.rare_threshold:
            description_pool = rare_descriptions
        else:
            description_pool = descriptions
        description = random.choice(description_pool)
        embed = discord.Embed(
            title="Bot Status",
            description=description.format(name=inter.user.name or "User"),
            color=0x734EBE,
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        """Auto pin and respond to user message in support forum thread."""
        if thread.parent_id not in [1020114888720384032, 1027594394477539410]:
            return
        # start = await anext(
        #     thread.history(limit=1, oldest_first=True),
        # )
        # await start.pin()
        embed = discord.Embed(
            title="Support Ticket",
            description="We want to help you to the best of our ability, but first we have to ask"
            " and make sure you have taken the proper steps to installing"
            " SideStore before we can help.\n\n",
            color=0x734EBE,
        )
        embed.add_field(
            name="Ensure The WiFi AND VPN Are On",
            value="Without WiFi **AND** the WireGuard VPN, SideStore cannot function correctly."
            " Try toggling the VPN a few times.",
            inline=True,
        )
        embed.add_field(
            name="Ensure You Don't Have AltStore",
            value="If you have AltStore installed as well as SideStore, you will only be able to install"
            " 1 or **NO** apps in SideStore!",
            inline=True,
        )
        embed.add_field(
            name="Ensure Your Anisette Server Works",
            value="If you are using the official SideStore server you can "
            "check https://ani.sidestore.io/ in Safari for a text output."
            "If there is no output, ping a Project Developer immediately!\n\n",
            inline=False,
        )
        embed.add_field(
            name="Provide SideStore Log Files or Screenshots",
            value="Please provide as much information about the error you are experiencing. You can "
            "send the `minimuxer.log` file from inside Files > SideStore as well as in-app"
            " screenshots, and that would help us diagnose your issues much faster!\n",
            inline=False,
        )
        embed.add_field(
            name="Finally, The Hardest Requirement...",
            value="Patience! Please have patience with our Helpers and Developer staff, we are all"
            " open source maintainers who do all of this for free on our own time. Thank you!",
            inline=False,
        )
        await thread.send(embed=embed)


async def setup(bot: Bot) -> None:
    """Set up Utility cog with bot."""
    await bot.add_cog(Utility(bot))
