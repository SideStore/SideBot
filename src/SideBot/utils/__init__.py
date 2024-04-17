"""utilites for SideBot."""

import discord


class DiscordUser:
    """DiscordUser class."""

    def __init__(self, iden: int, name: str) -> None:
        """DiscordUser class."""
        self.id = iden
        self.name = name

    @classmethod
    def to_tuple(cls, user: "DiscordUser") -> tuple[int, str]:
        """Convert to tuple."""
        return user.id, user.name

    @classmethod
    def from_tuple(cls, user: tuple[int, str]) -> "DiscordUser":
        """Convert from tuple."""
        return cls(*user)

    @classmethod
    def from_dpy_user(cls, user: discord.User | discord.Member) -> "DiscordUser":
        """Convert from discord.py User."""
        return cls(user.id, user.name)


class ButtonLink:
    """ButtonLink class."""

    def __init__(self, label: str, url: str) -> None:
        """ButtonLink class."""
        self.label = label
        self.url = url

    @classmethod
    def to_tuple(cls, button: "ButtonLink") -> tuple[str, str]:
        """Convert to tuple."""
        return button.label, button.url

    @classmethod
    def from_tuple(cls, button: tuple[str, str]) -> "ButtonLink":
        """Convert from tuple."""
        return cls(*button)
