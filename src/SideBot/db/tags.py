import psycopg2

class _Tags:
    def __init__(self, conn: psycopg2.extensions.connection):
        self.conn = conn
        self.cursor = conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tags (guild_id BIGINT, name TEXT, content TEXT)")

    def get(self, guild_id: int, tag_name: str):
        self.cursor.execute("SELECT content FROM tags WHERE guild_id = %s AND name = %s", (guild_id, tag_name))
        return self.cursor.fetchone()

    def get_all(self, guild_id: int):
        self.cursor.execute("SELECT name, content FROM tags WHERE guild_id = %s", (guild_id,))
        return self.cursor.fetchall()

    def create(self, guild_id: int, tag_name: str, content: str):
        self.cursor.execute("INSERT INTO tags (guild_id, name, content) VALUES (%s, %s, %s)", (guild_id, tag_name, content))
        self.conn.commit()

    def delete(self, guild_id: int, tag_name: str):
        self.cursor.execute("DELETE FROM tags WHERE guild_id = %s AND name = %s", (guild_id, tag_name))
        self.conn.commit()

    def update(self, guild_id: int, tag_name: str, content: str):
        self.cursor.execute("UPDATE tags SET content = %s WHERE guild_id = %s AND name = %s", (content, guild_id, tag_name))
        self.conn.commit()

class Tags:
    def __init__(self, tagname: str, content: str, conn: psycopg2.extensions.connection):
        self.tagname = tagname
        self.content = content
        self.tags = _Tags(conn)

    @classmethod
    def get(cls, guild_id: int, tag_name: str, conn: psycopg2.extensions.connection):
        return cls(tag_name, _Tags(conn).get(guild_id, tag_name), conn)
    
    @classmethod
    def get_all(cls, guild_id: int, conn):
        return [cls(tag_name, content, conn) for tag_name, content in _Tags(conn).get_all(guild_id)]
    
    def create(self, guild_id: int):
        self.tags.create(guild_id, self.tagname, self.content)

    def delete(self, guild_id: int):
        self.tags.delete(guild_id, self.tagname)
    
    def update(self, guild_id: int):
        self.tags.update(guild_id, self.tagname, self.content)