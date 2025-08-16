from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional, Type, TypeVar, Callable, Tuple, Any, Generator
from uuid import UUID

from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session as SQLModelSession, Session

from pjdev_postgres import postgres_settings, concurrency_service
from pjdev_postgres.models import ConnectionOptions, Savable, History

T = TypeVar("T", bound=Savable)


class Context:
    engine: Optional[Engine] = None


__ctx = Context()


def initialize_engine(
        tables: List[Type[SQLModel]],
        options: Optional[ConnectionOptions] = None,
        create_tables: bool = False,
) -> Engine:
    if options is None:
        options = ConnectionOptions()

    settings = postgres_settings.get_settings()

    if len(tables) == 0:
        raise ValueError("Must specify at least one table")

    db_url = settings.get_url()

    engine = create_engine(
        db_url,
        echo=options.echo,
        pool_size=options.pool_size,
        max_overflow=options.max_overflow,
    )

    if create_tables:
        for t in tables:
            t.__table__.create(bind=engine, checkfirst=True)

    return engine


def configure_single_context(
        tables: List[Type[SQLModel]], options: Optional[ConnectionOptions] = None
):
    __ctx.engine = initialize_engine(tables, options)


@contextmanager
def session_context() -> Generator[Session, Any, None]:
    with SQLModelSession(__ctx.engine) as session:
        try:
            yield session
        finally:
            session.close()


def get_session() -> Generator[Session, Any, None]:
    with SQLModelSession(__ctx.engine) as session:
        yield session


def create_new(
        obj: T,
        session: SQLModelSession,
        commit: bool = True,
        user_resolver: Callable[[], Tuple[Optional[str], str]] = lambda: ('anonymous_id', 'anonymous_name'),
) -> T:
    new_obj = concurrency_service.validate_version(obj)
    session.add(new_obj)
    user_oid, username = user_resolver()
    new_obj.created_by_id = user_oid
    new_obj.created_by = username

    if commit:
        session.commit()
        session.refresh(new_obj)

    return new_obj


def save(
        obj: T,
        session: SQLModelSession,
        concurrency_token: Optional[UUID] = None,
        commit: bool = True,
        user_resolver: Callable[[], Tuple[Optional[str], str]] = lambda: ('anonymous_id', 'anonymous_name'),
) -> T:
    updated_obj = concurrency_service.validate_version(obj, concurrency_token)
    updated_obj.last_modified_datetime = datetime.now(timezone.utc)
    user_oid, username = user_resolver()
    updated_obj.last_modified_by_id = user_oid
    updated_obj.last_modified_by = username

    session.flush([updated_obj])

    history = History(
        entity_name=updated_obj.__class__.__name__.lower(),
        entity_id=updated_obj.id,
        value=updated_obj.model_dump_json(),
    )
    session.add(history)

    if commit:
        session.commit()
        session.refresh(updated_obj)

    return updated_obj
