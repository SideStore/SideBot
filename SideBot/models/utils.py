import sqlite3
import asyncio
import aiosqlite
from typing import TypeVar
from types import SimpleNamespace
from collections import namedtuple


class classproperty:
    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        _ = instance
        return self.fget(owner)


class BaseModel:
    __table__ = {
        "name": "OVERRIDE ME",
        "pk": "id",
        "create": "OVERRIDE ME",
        "drop": "OVERRIDE ME",
        "select": "OVERRIDE ME",
        "insert": "OVERRIDE ME",
        "where": "OVERRIDE ME",
        "update": "OVERRIDE ME",
        "delete": "OVERRIDE ME",
    }
    _table = namedtuple("table", ["name", "pk", "create", "drop", "select", "insert", "where", "update", "delete"])

    def __init__(self, *_): ...

    @classmethod
    def from_db(cls, d: tuple | aiosqlite.Row | None):
        _ = d
        raise NotImplementedError("This class is meant to be a base template, subclasses must implement!")

    def to_db(self) -> tuple:
        raise NotImplementedError("This class is meant to be a base template, subclasses must implement!")

    @property
    def _ins(self):
        return (self._t.insert, self.to_db())

    @property
    def _upd(self):
        return (
            f"{self._t.update} {self._t.where}",
            (
                *self.to_db()[1:],
                self._pk,
            ),
        )

    @property
    def _del(self):
        return (f"{self._t.delete} {self._t.where}", (self._pk,))

    @property
    def _pk(self):
        return getattr(self, self.__table__["pk"])

    @classproperty
    def _t(cls) -> _table:
        return cls._table(**cls.__table__)


B = TypeVar("B", bound=BaseModel)


class ModelManager:
    def __init__(self, file: str):
        self._f = file
        self._conn = sqlite3.connect(self._f)
        self._conn.execute("PRAGMA foreign_keys = 1")

    def __repr__(self):
        return f"{self.__class__.__name__}(sqlite3.Connection({self._f!r}))"

    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()

    def close(self) -> None:
        return self._conn.close()

    def commit(self, cur: sqlite3.Cursor | None = None) -> None:
        if cur is not None:
            cur.close()
        return self._conn.commit()

    def register(self, model: type[B] | list[type[B]]):
        cur = self.cursor()
        if isinstance(model, list):
            for m in model:
                cur.execute(m._t.create)
        else:
            cur.execute(model._t.create)
        return self.commit(cur)

    def drop(self, model: type[B] | list[type[B]]):
        cur = self.cursor()
        if isinstance(model, list):
            for m in model:
                cur.execute(m._t.drop)
        else:
            cur.execute(model._t.drop)
        return self.commit(cur)

    def fetch_model(self, model: type[B], where: tuple[str, tuple] | None = None) -> B:
        cur = self.cursor()
        if where is None:
            cur.execute(model._t.select)
        else:
            cur.execute(model._t.select + " " + where[0], where[1])
        ret = model.from_db(cur.fetchone())
        cur.close()
        return ret

    def fetch_models(self, model: type[B], where: tuple[str, tuple] | None = None) -> list[B]:
        cur = self.cursor()
        if where is None:
            cur.execute(model._t.select)
        else:
            cur.execute(model._t.select + " " + where[0], where[1])
        ret = [model.from_db(d) for d in cur.fetchall()]
        cur.close()
        return ret

    def insert_model(self, model: B | list[B]):
        cur = self.cursor()
        if isinstance(model, list):
            for m in model:
                cur.execute(*m._ins)
        else:
            cur.execute(*model._ins)
        self.commit(cur)

    def update(self, model: B | list[B]):
        cur = self.cursor()
        if isinstance(model, list):
            for m in model:
                cur.execute(*m._upd)
        elif isinstance(model, BaseModel):
            cur.execute(*model._upd)
        self.commit(cur)

    def delete(self, model: B | list[B]):
        cur = self.cursor()
        if isinstance(model, list):
            for m in model:
                cur.execute(*m._del)
        elif isinstance(model, BaseModel):
            cur.execute(*model._del)
        self.commit(cur)


class AsyncModelManager:
    @classmethod
    async def from_file(cls, file: str):
        conn = await aiosqlite.connect(file)
        await conn.execute("PRAGMA foreign_keys = 1")
        return cls(conn, file)

    def __init__(self, conn: aiosqlite.Connection, file: str):
        self._f = file
        self._conn = conn

    def __repr__(self):
        return f"{self.__class__.__name__}(sqlite3.Connection({self._f!r}))"

    async def cursor(self) -> aiosqlite.Cursor:
        return await self._conn.cursor()

    async def close(self) -> None:
        return await self._conn.close()

    async def commit(self, cur: aiosqlite.Cursor | None = None) -> None:
        if cur is not None:
            await cur.close()
        return await self._conn.commit()

    async def register(self, model: type[B] | list[type[B]]):
        cur = await self.cursor()
        if isinstance(model, list):
            await asyncio.gather(*[cur.execute(m._t.create) for m in model])
        else:
            await cur.execute(model._t.create)
        return await self.commit(cur)

    async def drop(self, model: type[B] | list[type[B]]):
        cur = await self.cursor()
        if isinstance(model, list):
            await asyncio.gather(*[cur.execute(m._t.drop) for m in model])
        else:
            await cur.execute(model._t.drop)
        return await self.commit(cur)

    async def fetch_model(self, m: type[B], where: tuple[str, tuple] | None = None) -> B | None:
        cur = await self.cursor()
        if where is None:
            await cur.execute(m._t.select)
        else:
            await cur.execute(m._t.select + " " + where[0], where[1])
        if (r := await cur.fetchone()) is None:
            return r
        ret = m.from_db(r)
        await cur.close()
        return ret

    async def fetch_models(self, m: type[B], where: tuple[str, tuple] | None = None) -> list[B]:
        cur = await self.cursor()
        if where is None:
            await cur.execute(m._t.select)
        else:
            await cur.execute(m._t.select + " " + where[0], where[1])
        ret = [m.from_db(d) for d in await cur.fetchall()]
        await cur.close()
        return ret

    async def insert_model(self, model: B | list[B]):
        cur = await self.cursor()
        if isinstance(model, list):
            await asyncio.gather(*[cur.execute(*m._ins) for m in model])
        else:
            await cur.execute(*model._ins)
        await self.commit(cur)

    async def update(self, new: B | list[B]):
        cur = await self.cursor()
        if isinstance(new, list):
            await asyncio.gather(*[cur.execute(*m._upd) for m in new])
        elif isinstance(new, BaseModel):
            await cur.execute(*new._upd)
        await self.commit(cur)

    async def delete(self, new: B | list[B]):
        cur = await self.cursor()
        if isinstance(new, list):
            await asyncio.gather(*[cur.execute(*m._del) for m in new])
        elif isinstance(new, BaseModel):
            await cur.execute(*new._del)
        await self.commit(cur)
