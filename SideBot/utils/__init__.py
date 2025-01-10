"""utilites for SideBot."""

import discord


class DBConfig:
    """DBConfig class for Postgresql with Bot"""

    __slot__ = ("user", "password", "host", "port", "name")

    def __init__(self, user: str, password: str, host: str, port: int | None = None, name: str | None = None):
        self.user = user
        self.password = password
        self.host = host
        self.port = port or 5432
        self.name = name or user

    @property
    def connect_str(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def as_dict(self):
        return {
            "user": self.user,
            "pass": self.password,
            "host": self.host,
            "port": self.port,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DBConfig":
        return cls(
            data["user"],
            data["pass"],
            data["host"],
            data["port"] if "port" in data else None,
            data["name"] if "name" in data else data["user"],
        )


class BotConfig:
    """BotConfig class for SideBot"""

    __slots__ = ("token", "owner", "db_url", "cogs")

    def __init__(self, token: str, owner: int, db_url: str, cogs: list[str]):
        self.token = token
        self.owner = owner
        self.db_url = db_url
        self.cogs = cogs

    @classmethod
    def from_dict(cls, data: dict) -> "BotConfig":
        if "botDB" in data:
            return cls(data["discordToken"], data["owner"], DBConfig.from_dict(data["botDB"]).connect_str, data["cogs"])
        return cls(data["discordToken"], data["owner"], data["botDBURL"], data["cogs"])


class DiscordUser:
    """DiscordUser class."""

    def __init__(self, iden: int, name: str) -> None:
        """DiscordUser class."""
        self.id = iden
        self.name = name

    def to_tuple(self) -> tuple[int, str]:
        """Convert to tuple."""
        return self.id, self.name

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
