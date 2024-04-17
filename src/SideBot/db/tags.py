"""Tags database module."""

import datetime
from collections.abc import AsyncGenerator
from typing import Any

import asyncpg

from SideBot.utils import ButtonLink, DiscordUser


class _Tags:
    """Internal DB class for tags."""

    async def write_schema(self) -> None:
        for x in [
            """
            CREATE TYPE public.discorduser AS (
                id BIGINT,
                name TEXT
            )
            """,
            """
            CREATE TYPE public.buttonlink AS (
                label TEXT,
                url TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                guild_id BIGINT,
                id SERIAL PRIMARY KEY NOT NULL UNIQUE,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                author discorduser NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                button_links buttonlink[],
                used BIGINT DEFAULT 0
            )
            """,
            "CREATE INDEX IF NOT EXISTS tags_guild_id_idx ON tags (guild_id, name)",
        ]:
            await self.conn.execute(
                x,
            )

    def __init__(self, conn: asyncpg.Connection) -> None:
        """Tag database operations."""
        self.conn: asyncpg.Connection = conn

    async def get(self, guild_id: int, tag_name: str) -> asyncpg.Record | None:
        """Get a tag."""
        return await self.conn.fetchrow(
            "SELECT * FROM tags WHERE guild_id = $1 AND name = $2",
            guild_id,
            tag_name,
        )

    async def get_all(
        self,
        guild_id: int,
    ) -> AsyncGenerator[asyncpg.Record, asyncpg.Record]:
        """Get all tags."""
        fetchrow = await self.conn.fetch(
            "SELECT name, content, author, created_at, updated_at, button_links, used FROM tags WHERE guild_id = $1",
            guild_id,
        )
        for row in fetchrow:
            yield row

    async def create(
        self,
        guild_id: int,
        tag_name: str,
        content: str,
        author: DiscordUser,
        button_links: list[ButtonLink],
        used: int = 0,
    ) -> None:
        """Create a tag."""
        await self.conn.execute(
            """INSERT INTO tags
            (guild_id, name, content, author, button_links, used)
            VALUES
            ($1, $2, $3, $4, $5, $6)""",
            guild_id,
            tag_name,
            content,
            author,
            button_links,
            used,
        )

    async def delete(self, guild_id: int, tag_name: str) -> None:
        """Delete a tag."""
        await self.conn.execute(
            "DELETE FROM tags WHERE guild_id = $1 AND name = $2",
            guild_id,
            tag_name,
        )

    async def update(self, guild_id: int, tag_name: str, content: str) -> None:
        """Update a tag."""
        await self.conn.execute(
            "UPDATE tags SET content = $1, updated_at = $4 WHERE guild_id = $2 AND name = $3",
            content,
            guild_id,
            tag_name,
            datetime.datetime.now(tz=datetime.UTC),
        )

    async def update_used_count(self, guild_id: int, tag_name: str) -> None:
        """Update used count."""
        await self.conn.execute(
            "UPDATE tags SET used = used + 1 WHERE guild_id = $1 AND name = $2",
            guild_id,
            tag_name,
        )


class Tag:
    """Tag class."""

    def __init__(
        self,
        tagname: str,
        content: str,
        author: DiscordUser,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        button_links: list[ButtonLink],
        used_count: int,
        conn: asyncpg.Connection,
    ) -> None:
        """Tag class."""
        self.tagname = tagname
        self.content = content
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at
        self.button_links = button_links
        self.used_count = used_count
        self.tags = _Tags(conn)

    async def finish(
        self,
    ) -> "Tag":
        """Tag class."""
        await self.tags.write_schema()
        return self

    @classmethod
    async def get(
        cls,
        guild_id: int,
        tag_name: str,
        conn: asyncpg.Connection,
    ) -> "Tag":
        """Get a tag."""
        tag = await _Tags(conn).get(guild_id, tag_name)
        if not tag:
            msg = f"Tag {tag_name} not found"
            raise ValueError(msg)
        await _Tags(conn).update_used_count(guild_id, tag_name)
        return cls(
            tag_name,
            tag["content"],
            tag["author"],
            tag["created_at"],
            tag["updated_at"],
            tag["button_links"],
            tag["used"],
            conn,
        )

    @classmethod
    async def get_all(
        cls,
        guild_id: int,
        conn: asyncpg.Connection,
    ) -> AsyncGenerator["Tag", Any]:
        """Get all tags."""
        async for tag in _Tags(conn).get_all(guild_id):
            yield cls(
                tag["name"],
                tag["content"],
                tag["author"],
                tag["created_at"],
                tag["updated_at"],
                tag["button_links"],
                tag["used"],
                conn,
            )

    async def create(self, guild_id: int) -> None:
        """Create a tag."""
        await self.tags.create(
            guild_id,
            self.tagname,
            self.content,
            self.author,
            self.button_links,
            self.used_count,
        )

    async def delete(self, guild_id: int) -> None:
        """Delete a tag."""
        await self.tags.delete(guild_id, self.tagname)

    async def update(self, guild_id: int) -> None:
        """Update a tag."""
        await self.tags.update(guild_id, self.tagname, self.content)
