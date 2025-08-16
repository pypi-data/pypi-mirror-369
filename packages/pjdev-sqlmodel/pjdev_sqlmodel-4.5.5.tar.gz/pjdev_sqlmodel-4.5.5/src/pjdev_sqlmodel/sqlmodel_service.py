from contextlib import contextmanager
from typing import (
    Optional,
    Type,
    List,
)

from sqlalchemy import Engine
from sqlmodel import create_engine, Session as SQLModelSession

from .models import ModelBase, TOptions, TSettings


class DBContext:
    initialized: bool = False
    engine: Optional[Engine] = None


__ctx = DBContext()


def initialize_engine(
    settings: TSettings,
    opts: TOptions,
    tables: Optional[List[Type[ModelBase]]] = None,
) -> Engine:
    database_url = settings.get_connection_string()

    engine = create_engine(database_url, **opts.model_dump())

    if tables is not None:
        for t in tables:
            t.__table__.create(bind=engine, checkfirst=True)

    return engine


def configure_single_context(
    settings: TSettings, opts: TOptions, tables: List[Type[ModelBase]]
):
    __ctx.engine = initialize_engine(settings, opts=opts, tables=tables)


def get_engine() -> Engine:
    if __ctx.engine is None:
        raise ValueError("No engine has been initialized")
    return __ctx.engine


@contextmanager
def session_context() -> SQLModelSession:
    with SQLModelSession(__ctx.engine) as session:
        try:
            yield session
        finally:
            session.close()
