import json

import arrow
from arrow import Arrow
import aiosqlite

from .utils import BaseModel, ModelManager, AsyncModelManager


class Tag(BaseModel):
    __table__ = {
        "name": "tag",
        "pk": "tid",
        "create": "CREATE TABLE IF NOT EXISTS tag ( id INTEGER PRIMARY KEY, guild INTEGER DEFAULT NULL, "
        "name TEXT NOT NULL, content TEXT NOT NULL, author INTEGER NOT NULL, "
        "display TEXT NOT NULL DEFAULT 'embed', color INTEGER NOT NULL DEFAULT 7556798, "
        "created INTEGER NOT NULL DEFAULT (strftime('%s', 'now')), "
        "updated INTEGER NOT NULL DEFAULT (strftime('%s', 'now')), buttons TEXT DEFAULT NULL, "
        "used INTEGER NOT NULL DEFAULT 0, UNIQUE (guild, name) )",
        "drop": "DROP TABLE tag",
        "select": "SELECT name, content, author, id, guild, display, color, created, updated, buttons, used FROM tag",
        "insert": "INSERT INTO tag (id, name, content, author, guild, display, color, created, updated, buttons, used) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "where": "WHERE id = ?",
        "update": "UPDATE tag SET name = ?, content = ?, author = ?, guild = ?, display = ?, color = ?, created = ?, "
        "updated = ?, buttons = ?, used = ?",
        "delete": "DELETE FROM tag",
    }

    def __init__(
        self,
        name: str,
        content: str,
        author: int,
        tid: int | None = None,
        guild: int | None = None,
        display: str = "embed",
        color: int = 0x734EBE,
        created: Arrow | None = None,
        updated: Arrow | None = None,
        buttons: list[dict[str, str]] | None = None,
        used: int = 0,
    ):
        self.tid = tid
        self.name = name
        self.content = content
        self.author = author
        self.guild = guild
        self.display = display
        self.color = color
        self.created = arrow.now() if created is None else created
        self.updated = self.created if updated is None else updated
        self.buttons = [] if buttons is None else buttons
        self.used = used

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.tid}, {self.name!r}, {self.author}, {self.created!r}, "
            f"{self.updated!r}, {self.used!r})"
        )

    @classmethod
    def from_db(cls, d: tuple | aiosqlite.Row | None):
        if d is None:
            return d
        return cls(
            d[0],  # name
            d[1],  # content
            d[2],  # author
            d[3],  # tid
            d[4],  # guild
            d[5],  # display
            d[6],  # color
            arrow.get(d[7]),  # created
            arrow.get(d[8]),  # updated
            d[9] if d[9] is None else json.loads(d[9]),  # buttons
            d[10],  # used
        )

    def to_db(self):
        return (
            self.tid,
            self.name,
            self.content,
            self.author,
            self.guild,
            self.display,
            self.color,
            int(self.created.timestamp()),
            int(self.updated.timestamp()),
            json.dumps(self.buttons),
            self.used,
        )


class TagManager(ModelManager):
    def __init__(self, file: str):
        super().__init__(file)
        self.register(Tag)

    @property
    def tags(self):
        return self.fetch_models(Tag)


class AsyncTagManager(AsyncModelManager):
    @classmethod
    async def from_file(cls, file: str):
        s = await super().from_file(file)
        await s.register(Tag)
        return s

    def __init__(self, conn: aiosqlite.Connection, file: str):
        super().__init__(conn, file)

    @property
    async def tags(self):
        return await self.fetch_models(Tag)

    async def tag(self, *, tid: int | None = None, name: str | None = None, guild: int | None = None):
        if tid is not None:
            return next((t for t in await self.tags if t.tid == tid), None)
        if name is not None:
            if guild is not None:
                return next((t for t in await self.tags if t.name == name and t.guild == guild), None)
            return next((t for t in await self.tags if t.name == name), None)
        if guild is not None:
            return next((t for t in await self.tags if t.guild == guild), None)
