"""Tags database module."""

import contextlib
import datetime
from collections.abc import AsyncGenerator
from typing import Any

import asyncpg

from SideBot.utils import ButtonLink, DiscordUser


class _Tags:
    """Internal DB class for tags."""

    @staticmethod
    async def write_schema(conn: asyncpg.Connection) -> None:
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
            with contextlib.suppress(asyncpg.exceptions.DuplicateObjectError):
                await conn.execute(
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
            "SELECT * FROM tags WHERE guild_id = $1",
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

    async def save(
        self,
        tag_id: int,
        guild_id: int,
        tag_name: str,
        content: str,
        author: DiscordUser,
        button_links: list[ButtonLink],
        used: int = 0,
    ) -> None:
        """Save a tag."""
        await self.conn.execute(
            """UPDATE tags SET
            guild_id = $1, name = $2, content = $3, author = $4, button_links = $5, used = $6
            WHERE id = $7 """,
            guild_id,
            tag_name,
            content,
            author,
            button_links,
            used,
            tag_id,
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
            datetime.datetime.now(),  # noqa: DTZ005
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
        guild_id: int,
        tagname: str,
        content: str,
        author: DiscordUser,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        button_links: list[ButtonLink],
        used_count: int,
        ident: int | None,
        conn: asyncpg.Connection,
    ) -> None:
        """Tag class."""
        self.guildid = guild_id
        self.tagname = tagname
        self.content = content
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at
        self.button_links = button_links
        self.used_count = used_count
        self.id = ident
        self.tags = _Tags(conn)

    @staticmethod
    async def write_schema(
        conn: asyncpg.Connection,
    ) -> None:
        """Tag class."""
        await _Tags.write_schema(conn)

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
            guild_id,
            tag_name,
            tag["content"],
            tag["author"],
            tag["created_at"],
            tag["updated_at"],
            tag["button_links"],
            tag["used"],
            tag["id"],
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
                guild_id,
                tag["name"],
                tag["content"],
                tag["author"],
                tag["created_at"],
                tag["updated_at"],
                tag["button_links"],
                tag["used"],
                tag["id"],
                conn,
            )

    async def create(self) -> None:
        """Create a tag."""
        await self.tags.create(
            self.guildid,
            self.tagname,
            self.content,
            self.author,
            self.button_links,
            self.used_count,
        )

    async def delete(self) -> None:
        """Delete a tag."""
        await self.tags.delete(self.guildid, self.tagname)

    async def update(self) -> None:
        """Update a tag."""
        await self.tags.update(self.guildid, self.tagname, self.content)

    async def save(self) -> None:
        """Save a tag."""
        if not self.id:
            return await self.create()
        await self.tags.save(
            self.id,
            self.guildid,
            self.tagname,
            self.content,
            self.author,
            self.button_links,
            self.used_count,
        )
        return None
