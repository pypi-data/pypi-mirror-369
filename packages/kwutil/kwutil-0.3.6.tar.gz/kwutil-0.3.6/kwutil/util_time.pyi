import datetime
from datetime import datetime as datetime_cls

import pint
from datetime import tzinfo

__docstubs__: str


class TimeValueError(ValueError):
    ...


class TimeTypeError(TypeError):
    ...


def isoformat(dt: datetime_cls,
              sep: str = ...,
              timespec: str = ...,
              pathsafe: bool = True):
    ...


def coerce_datetime(
        data,
        default_timezone: str = 'utc',
        nan_policy: str = 'return-None',
        none_policy: str = 'return-None') -> datetime.datetime | None:
    ...


def coerce_timedelta(delta: str | int | float) -> datetime.timedelta:
    ...


def coerce_timezone(tz: str | tzinfo) -> tzinfo:
    ...


def ensure_timezone(dt: datetime.datetime,
                    default: str = 'utc') -> datetime.datetime:
    ...


def format_timedelta(delta: datetime.timedelta,
                     resolution: datetime.timedelta | str | None = None,
                     unit: str | None | pint.Unit = None,
                     precision: int | None = None) -> str:
    ...
