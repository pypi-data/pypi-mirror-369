from typing import TypeVar, Optional
from uuid import UUID, uuid4
from loguru import logger

from pjdev_postgres.models import Versioned, ConcurrencyException

T = TypeVar("T", bound=Versioned)


def parse_concurrency_token(token: str) -> Optional[UUID]:
    try:
        concurrency_token = UUID(token) if token is not None else None
        return concurrency_token
    except TypeError as e:
        logger.warning(f"{e}")
        logger.warning(f"Tried parsing invalid uuid: {token}")


def increment_version(obj: T) -> T:
    obj.concurrency_token = uuid4()

    return obj


def validate_version(obj: T, token: Optional[str | UUID] = None) -> T:
    concurrency_token = token
    if not isinstance(token, UUID):
        concurrency_token = parse_concurrency_token(token)

    if obj.concurrency_token is not None and obj.concurrency_token != concurrency_token:
        raise ConcurrencyException("Stale data detected")

    return increment_version(obj)
