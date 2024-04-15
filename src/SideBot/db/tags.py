"""Tags database module."""

from typing import Any

import psycopg2


class _Tags:
    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        """Tag database operations."""
        self.conn = conn
        self.cursor = conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tags (guild_id BIGINT, name TEXT, content TEXT)",
        )

    def get(self, guild_id: int, tag_name: str) -> tuple[Any, ...] | None:
        """Get a tag."""
        self.cursor.execute(
            "SELECT content FROM tags WHERE guild_id = %s AND name = %s",
            (guild_id, tag_name),
        )
        return self.cursor.fetchone()

    def get_all(self, guild_id: int) -> list[tuple[Any, ...]]:
        """Get all tags."""
        self.cursor.execute(
            "SELECT name, content FROM tags WHERE guild_id = %s",
            (guild_id,),
        )
        return self.cursor.fetchall()

    def create(self, guild_id: int, tag_name: str, content: str) -> None:
        """Create a tag."""
        self.cursor.execute(
            "INSERT INTO tags (guild_id, name, content) VALUES (%s, %s, %s)",
            (guild_id, tag_name, content),
        )
        self.conn.commit()

    def delete(self, guild_id: int, tag_name: str) -> None:
        """Delete a tag."""
        self.cursor.execute(
            "DELETE FROM tags WHERE guild_id = %s AND name = %s",
            (guild_id, tag_name),
        )
        self.conn.commit()

    def update(self, guild_id: int, tag_name: str, content: str) -> None:
        """Update a tag."""
        self.cursor.execute(
            "UPDATE tags SET content = %s WHERE guild_id = %s AND name = %s",
            (content, guild_id, tag_name),
        )
        self.conn.commit()


class Tag:
    """Tag class."""

    def __init__(
        self,
        tagname: str,
        content: str,
        conn: psycopg2.extensions.connection,
    ) -> None:
        """Tag class."""
        self.tagname = tagname
        self.content = content
        self.tags = _Tags(conn)

    @classmethod
    def get(cls, guild_id: int, tag_name: str, conn: psycopg2.extensions.connection) -> "Tag":
        """Get a tag."""
        tag = _Tags(conn).get(guild_id, tag_name)
        if not tag:
            msg = f"Tag {tag_name} not found"
            raise ValueError(msg)
        return cls(tag_name, tag[0], conn)

    @classmethod
    def get_all(cls, guild_id: int, conn: psycopg2.extensions.connection) -> list["Tag"]:
        """Get all tags."""
        return [cls(tag_name, content, conn) for tag_name, content in _Tags(conn).get_all(guild_id)]

    def create(self, guild_id: int) -> None:
        """Create a tag."""
        self.tags.create(guild_id, self.tagname, self.content)

    def delete(self, guild_id: int) -> None:
        """Delete a tag."""
        self.tags.delete(guild_id, self.tagname)

    def update(self, guild_id: int) -> None:
        """Update a tag."""
        self.tags.update(guild_id, self.tagname, self.content)
