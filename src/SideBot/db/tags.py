"""Tags database module."""

import asyncio
from typing import Any, AsyncGenerator
import datetime

import asyncpg


class _Tags:
    def __init__(self, conn: asyncpg.Connection) -> None:
        """Tag database operations."""
        self.conn = conn
        tasks = set()
        for x in [
            """
            CREATE TYPE IF NOT EXISTS discorduser AS (
                id BIGINT,
                name TEXT
            )
            """,
            """
            CREATE TYPE IF NOT EXISTS buttonlink AS (
                label TEXT,
                url TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                guild_id BIGINT,
                name TEXT UNIQUE PRIMARY KEY,
                content TEXT,
                author BIGINT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                button_links buttonlink[],
                used BIGINT DEFAULT 0
            )
            """,
            "CREATE INDEX IF NOT EXISTS tags_guild_id_idx ON tags (guild_id, name)",
        ]:
            task = asyncio.create_task(
                self.conn.cursor(
                    x,
                ),
            )
            tasks.add(task)
            task.add_done_callback(lambda _: tasks.remove(task))
        task = asyncio.create_task(
            self.conn.set_type_codec(
                "discorduser",
                encoder=DiscordUser.to_tuple,
                decoder=DiscordUser.from_tuple,
                format="tuple",
            )
        )
        tasks.add(task)
        task.add_done_callback(lambda _: tasks.remove(task))
        task = asyncio.create_task(
            self.conn.set_type_codec(
                "buttonlink",
                encoder=ButtonLink.to_tuple,
                decoder=ButtonLink.from_tuple,
                format="tuple",
            )
        )
        tasks.add(task)
        task.add_done_callback(lambda _: tasks.remove(task))

    async def get(self, guild_id: int, tag_name: str) -> asyncpg.Record | None:
        """Get a tag."""
        cursor = await self.conn.cursor(
            "SELECT content FROM tags WHERE guild_id = %s AND name = %s",
            (guild_id, tag_name),
        )
        return await cursor.fetchrow()

    async def get_all(self, guild_id: int) -> AsyncGenerator[asyncpg.Record, asyncpg.Record]:
        """Get all tags."""
        cursor = await self.conn.cursor(
            "SELECT content FROM tags WHERE guild_id = %s",
            (guild_id),
        )
        for row in await cursor:
            yield row

    async def create(self, guild_id: int, tag_name: str, content: str) -> None:
        """Create a tag."""
        await self.conn.cursor(
            "INSERT INTO tags (guild_id, name, content) VALUES (%s, %s, %s)",
            (guild_id, tag_name, content),
        )

    async def delete(self, guild_id: int, tag_name: str) -> None:
        """Delete a tag."""
        await self.conn.cursor(
            "DELETE FROM tags WHERE guild_id = %s AND name = %s",
            (guild_id, tag_name),
        )

    async def update(self, guild_id: int, tag_name: str, content: str) -> None:
        """Update a tag."""
        await self.conn.cursor(
            "UPDATE tags SET content = %s WHERE guild_id = %s AND name = %s",
            (content, guild_id, tag_name),
        )

    async def update_used_count(self, guild_id: int, tag_name: str) -> None:
        """Update used count."""
        await self.conn.cursor(
            "UPDATE tags SET used = used + 1 WHERE guild_id = %s AND name = %s",
            (guild_id, tag_name),
        )

class DiscordUser:
    """DiscordUser class."""

    def __init__(self, id: int, name: str) -> None:
        """DiscordUser class."""
        self.id = id
        self.name = name

    @classmethod
    def to_tuple(cls, user: "DiscordUser") -> tuple[int, str]:
        """Convert to tuple."""
        return user.id, user.name
    
    @classmethod
    def from_tuple(cls, user: tuple[int, str]) -> "DiscordUser":
        """Convert from tuple."""
        return cls(*user)
    
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

class Tag:
    """Tag class."""

    def __init__(
        self,
        tagname: str,
        content: str,
        author: DiscordUser,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        button_links: list[dict[str, str]],
        conn: asyncpg.Connection,
    ) -> None:
        """Tag class."""
        self.tagname = tagname
        self.content = content
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at
        self.button_links = button_links
        self.tags = _Tags(conn)

    @classmethod
    async def get(
        cls, guild_id: int, tag_name: str, conn: asyncpg.Connection
    ) -> "Tag":
        """Get a tag."""
        tag = await _Tags(conn).get(guild_id, tag_name)
        if not tag:
            msg = f"Tag {tag_name} not found"
            raise ValueError(msg)
        await _Tags(conn).update_used_count(guild_id, tag_name)
        return cls(tag_name, tag["name"], tag["content"], tag["author"], tag["created_at"], tag["updated_at"], tag["button_links"], tag["used_count"], conn)

    @classmethod
    async def get_all(
        cls, guild_id: int, conn: asyncpg.Connection
    ) -> AsyncGenerator["Tag", Any]:
        """Get all tags."""
        async for tag in _Tags(conn).get_all(guild_id):
            yield cls(
                tag["name"], tag["content"], tag["author"], tag["created_at"], tag["updated_at"], tag["button_links"], tag["used_count"], conn
            )

    async def create(self, guild_id: int) -> None:
        """Create a tag."""
        await self.tags.create(guild_id, self.tagname, self.content)

    async def delete(self, guild_id: int) -> None:
        """Delete a tag."""
        await self.tags.delete(guild_id, self.tagname)

    async def update(self, guild_id: int) -> None:
        """Update a tag."""
        await self.tags.update(guild_id, self.tagname, self.content)
