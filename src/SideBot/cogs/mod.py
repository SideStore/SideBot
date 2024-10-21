import logging

import openai
from discord import Embed, Message
from discord.ext.commands import Bot, Cog

from .basecog import BaseCog


class CheckMessage(BaseCog):
    """CheckMessage cog with commands for moderation."""

    def __init__(self, bot: Bot) -> None:
        """Initialize the checkmessage cog."""
        super().__init__(bot)
        self.openai = openai.AsyncOpenAI(base_url="http://localhost:8080", api_key="none")
        self.logger.info("Connected to OpenAI API")

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Check the message for spam."""
        if message.channel.id == 1200508244909621289:
            return
        else:
            logging.info(message.channel.id)
        if message.author.bot:
            return
        if message.guild and message.guild.id != 949183273383395328:
            return
        if len(message.content) <= 1:
            return
        self.logger.info("Checking message %s", message.content)
        history_to_give = ""
        async for messages in message.channel.history(limit=3):
            if messages.id == message.id:
                continue
            history_to_give += f"{messages.author!s}: Start-Of-Message\n{messages.content}\nEnd-Of-Message\n\n"
        response = await self.openai.chat.completions.create(
            model="idk",
            messages=[
                {
                    "role": "system",
                    "content": 'You are a moderation bot checking if messages defame gender identities. Please respond with only a "YES", "MAYBE", or "NO" with a short reasoning',
                },
                {
                    "role": "user",
                    "content": "context:",
                },
                {
                    "role": "user",
                    "content": f"{history_to_give}",
                },
                {
                    "role": "user",
                    "content": "message:",
                },
                {
                    "role": "user",
                    "content": f"{message.author!s}: Start-Of-Message\n{message.content}\nEnd-Of-Message\n\n",
                },
            ],
            n=1,
            max_tokens=10,
        )
        self.logger.info("Response: %s", response.choices[0].message)
        if "YES" in response.choices[0].message.content:
            self.logger.info("Message breaks rules")
            await self.bot.get_channel(1200508244909621289).send(
                embed=Embed(
                    title="Message Breaks Rules",
                    description=f"Jump To Message: [Here]({message.jump_url}), Reasoning: {response.choices[0].message.content}",
                ),
            )
        elif "MAYBE" in response.choices[0].message.content:
            self.logger.info("Message possibly breaks rules")
            await self.bot.get_channel(1200508244909621289).send(
                embed=Embed(
                    title="Message Possibly Breaks Rules",
                    description=f"Jump To Message: [Here]({message.jump_url}), Reasoning: {response.choices[0].message.content}",
                ),
                silent=True,
            )

    @classmethod
    async def setup(cls, bot: Bot) -> None:
        """Initialize the cog and add it to the bot."""
        logging.getLogger(__name__).info("Initialized %s", cls.__name__)
        await bot.add_cog(cls(bot))


setup = CheckMessage.setup
