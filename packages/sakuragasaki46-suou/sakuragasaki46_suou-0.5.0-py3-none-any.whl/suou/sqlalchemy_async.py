"""
Helpers for asynchronous use of SQLAlchemy.

NEW 0.5.0

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from __future__ import annotations
from functools import wraps


from sqlalchemy import Engine, Select, func, select
from sqlalchemy.orm import DeclarativeBase, lazyload
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from flask_sqlalchemy.pagination import Pagination

from suou.exceptions import NotFoundError

class SQLAlchemy:
    """
    Drop-in (?) replacement for flask_sqlalchemy.SQLAlchemy()
    eligible for async environments

    NEW 0.5.0
    """
    base: DeclarativeBase
    engine: AsyncEngine
    _sessions: list[AsyncSession]
    NotFound = NotFoundError

    def __init__(self, model_class: DeclarativeBase):
        self.base = model_class
        self.engine = None
        self._sessions = []
    def bind(self, url: str):
        self.engine = create_async_engine(url)
    def _ensure_engine(self):
        if self.engine is None:
            raise RuntimeError('database is not connected')
    async def begin(self, *, expire_on_commit = False, **kw) -> AsyncSession:
        self._ensure_engine()
        ## XXX is it accurate?
        s = AsyncSession(self.engine, expire_on_commit=expire_on_commit, **kw)
        self._sessions.append(s)
        return s
    async def __aenter__(self) -> AsyncSession:
        return await self.begin()
    async def __aexit__(self, e1, e2, e3):
        ## XXX is it accurate?
        s = self._sessions.pop()
        if e1:
            await s.rollback()
        else:
            await s.commit()
        await s.close()
    async def paginate(self, select: Select, *, 
        page: int | None = None, per_page: int | None = None,
        max_per_page: int | None = None, error_out: bool = True,
        count: bool = True) -> AsyncSelectPagination:
        """
        Return a pagination. Analogous to flask_sqlalchemy.SQLAlchemy.paginate().
        """
        async with self as session:
            return AsyncSelectPagination(
                select = select,
                session = session,
                page = page,
                per_page=per_page, max_per_page=max_per_page,
                error_out=self.NotFound if error_out else None, count=count
            )
    async def create_all(self, *, checkfirst = True):
        """
        Initialize database
        """
        self._ensure_engine()
        self.base.metadata.create_all(
            self.engine, checkfirst=checkfirst
        )



class AsyncSelectPagination(Pagination):
    """
    flask_sqlalchemy.SelectPagination but asynchronous.

    Pagination is not part of the public API, therefore expect that it may break
    """

    async def _query_items(self) -> list:
        select_q: Select = self._query_args["select"]
        select = select_q.limit(self.per_page).offset(self._query_offset)
        session: AsyncSession = self._query_args["session"]
        out = (await session.execute(select)).scalars()
        return out

    async def _query_count(self) -> int:
        select_q: Select = self._query_args["select"]
        sub = select_q.options(lazyload("*")).order_by(None).subquery()
        session: AsyncSession = self._query_args["session"]
        out = (await session.execute(select(func.count()).select_from(sub))).scalar()
        return out

    def __init__(self,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: Exception | None = NotFoundError,
        count: bool = True,
        **kwargs):
        ## XXX flask-sqlalchemy says Pagination() is not public API.
        ## Things may break; beware.
        self._query_args = kwargs
        page, per_page = self._prepare_page_args(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=error_out,
        )

        self.page: int = page
        """The current page."""

        self.per_page: int = per_page
        """The maximum number of items on a page."""

        self.max_per_page: int | None = max_per_page
        """The maximum allowed value for ``per_page``."""

        self.items = None
        self.total = None
        self.error_out = error_out
        self.has_count = count

    async def __aiter__(self):
        self.items = await self._query_items()
        if self.items is None:
            raise RuntimeError('query returned None')
        if not self.items and self.page != 1 and self.error_out:
            raise self.error_out
        if self.has_count:
            self.total = await self._query_count()
        for i in self.items:
            yield i


def async_query(db: SQLAlchemy, multi: False):
    """
    Wraps a query returning function into an executor coroutine.

    The query function remains available as the .q or .query attribute.
    """
    def decorator(func):
        @wraps(func)
        async def executor(*args, **kwargs):
            async with db as session:
                result = await session.execute(func(*args, **kwargs))
                return result.scalars() if multi else result.scalar()
        executor.query = executor.q = func
        return executor
    return decorator
        

# Optional dependency: do not import into __init__.py
__all__ = ('SQLAlchemy', 'async_query')