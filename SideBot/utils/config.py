class DBConfig:
    def __init__(self, tags: str):
        self.tags = tags

    def __repr__(self):
        return f"{self.__class__.__name__}({self.tags!r})"


class SideBotConfig:
    "SideBotConfig helper class for SideBot"

    __slots__ = (
        "token",
        "owner",
        "db",
        "cogs",
    )

    def __init__(self, token: str, owner: int, db: DBConfig, cogs: list[str]):
        self.token = token
        self.owner = owner
        self.db = DBConfig(**db) if isinstance(db, dict) else db
        self.cogs = cogs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.owner}, {self.db!r}, {self.cogs!r})"
