from datetime import date, datetime, UTC
from typing import Callable, List, Optional, Type, Any
from loguru import logger
from pydantic import BeforeValidator


def make_date_validator(
    date_format: str, date_obj_type: Type[date | datetime] = datetime
) -> Callable[[str], Optional[date]]:
    def validator(v: Optional[Any]) -> Optional[date]:
        if not v:
            return None

        if isinstance(v, datetime):
            formatted_value = v
            if date_format == "iso":
                formatted_value = v.astimezone(UTC)
            return (
                formatted_value if date_obj_type is datetime else formatted_value.date()
            )

        if isinstance(v, date):
            return v

        if not isinstance(v, str):
            return None

        stripped_value = v.strip()

        if stripped_value in ["-", ""]:
            return None

        if date_format == "iso":
            value = datetime.fromisoformat(v).replace(tzinfo=UTC)
        else:
            value = datetime.strptime(v, date_format)
        return value.date() if date_obj_type is date else value

    return validator


def make_date_validator_for_formats(
    date_formats: List[str], date_obj_type: Type[date | datetime] = datetime
) -> Callable[[str], Optional[date]]:
    def validator(v: Optional[Any]) -> Optional[date]:
        for fmt in date_formats:
            try:
                return make_date_validator(fmt, date_obj_type)(v)
            except ValueError as e:
                logger.warning(e)
                continue

        return None

    return validator


date_validator = BeforeValidator(make_date_validator_for_formats(["iso"], datetime))
