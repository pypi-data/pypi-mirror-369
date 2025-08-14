"""
Enhanced classes from the :mod:`datetime` module to provide extra functionality
while maintaining full compatibility with the stdlib.


By default the new `datetime` and `timedelta` constructs can be used without
any external dependencies, but if they are available we provide extra
functionality by making use of:

    * :mod:`dateutil`.

    * :mod:`pint`.


Similar tools:

    :mod:`pendulum` - https://github.com/sdispater/pendulum - drop in replacement for datetime

    :mod:`arrow` - https://github.com/arrow-py/arrow - does not inherit from stdlib datetime classes

    :mod:`delorean` - https://github.com/myusuf3/delorean - older and unmaintained


TODO:
    - [ ] support other common classes pint quantities in timedelta.coerce
    - [ ] consider a limited ubelt port?
    - [ ] arrow support
    - [ ] pendulum support
    - [ ] optionally persist enhanced instances across operations (like add)
    - [ ] pytz support?
    - [ ] binary backend support
"""
import math
import numbers
import warnings

import datetime as datetime_mod
from datetime import datetime as datetime_cls
from datetime import timedelta as timedelta_cls

import ubelt as ub

try:
    from functools import cache  # Python 3.9+ only
except ImportError:
    from ubelt import memoize as cache

try:
    from line_profiler import profile
except ImportError:
    profile = ub.identity

__docstubs__ = """
import pint
from datetime import tzinfo
"""


class TimeValueError(ValueError):
    ...


class TimeTypeError(TypeError):
    ...


# TODO
# class time(datetime_mod.time):
#     """
#     """


class datetime(datetime_cls):
    """
    An enhanced datetime class.

    Inherits from and behaves as a superset of the standard library
    :class`datetime.datetime` class.

    ParentDocs:

        datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

        The year, month and day arguments are required. tzinfo may be None, or an
        instance of a tzinfo subclass. The remaining arguments may be ints.

    Notable changes include:

    * :func:`kwutil.timedelta.coerce` - a flexible constructor to reduce boilerplate for handling multiple input formats (great for CLI inputs).

    * :func:`kwutil.timedelta.random` - a constructor for generating a random time duration (great for tests!).

    * :func:`kwutil.timedelta.ensure_timezone` - creates a tz aware version if needed

    * :func:`kwutil.timedelta.isoformat` - extends parent isoformat with a pathsafe argument and other options

    * :func:`kwutil.timedelta.ensure_timezone` - adds a "reasonable" timezone if one doesn't already exist

    * A more concise __str__ and __repr__

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> import kwutil
        >>> self = kwutil.util_time.datetime.random()
        >>> print(f'self = {self!s}')
        >>> print(f'self = {self!r}')
    """
    # __slots__ = datetime_cls.__slots__

    @classmethod
    def coerce(cls, data, default_timezone='utc', nan_policy='return-None',
               none_policy='return-None', copy_policy='avoid'):
        """
        Create a datetime based on reasonable interpretation of the input.

        Parses a timestamp and always returns a timestamp with a timezone.
        If only a date is specified, the time is defaulted to 00:00:00
        If one is not discoverable a specified default is used.
        A nan or None input depends on nan_policy and none_policy.

        Args:
            data (None | str | datetime_mod.datetime | datetime_mod.date):
                data to interpret as a datetime

            default_timezone (str): defaults to utc.

            none_policy (str):
                Can be: 'return-None', 'return-nan', or 'raise'.
                See :func:`_handle_null_policy` for details.

            nan_policy (str):
                Can be: 'return-None', 'return-nan', or 'raise'.
                See :func:`_handle_null_policy` for details.

        Returns:
            datetime | None

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> from kwutil.util_time import datetime
            >>> self = datetime.coerce('1970-01-01')
            >>> print(self.isoformat())
            1970-01-01T00:00:00+00:00
        """
        self = _coerce_datetime(data,
                                default_timezone=default_timezone,
                                nan_policy=nan_policy,
                                none_policy=none_policy,
                                copy_policy=copy_policy,
                                cls=cls)
        return self

    @classmethod
    def random(cls, start=None, end=None, rng=None):
        """
        Create a datetime object with randomized parameters.

        Returns:
            datetime_mod.datetime

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> from kwutil import datetime
            >>> self = datetime.random(start='2010-01-01', end='2020-01-01', rng=0)
            >>> print(self.isoformat())
            2016-07-21T19:56:39+00:00
        """
        from kwutil.util_random import ensure_rng
        rng = ensure_rng(rng)
        min_ts = (cls.coerce(start) or datetime_cls(1, 1, 2, 0, 0)).timestamp()
        max_ts = (cls.coerce(end) or cls.max).timestamp()
        ts = rng.randint(int(min_ts), int(max_ts))
        default_timezone = 'utc'
        tz = coerce_timezone(default_timezone)
        self = cls.fromtimestamp(ts, tz=tz)
        return self

    def __str__(self):
        return self.isoformat()

    def __repr__(self):
        return f'DT({self.isoformat()})'

    def isoformat(self, sep='T', timespec='seconds', pathsafe=False):
        """
        A path-safe version of datetime_cls.isotime() that returns a
        path-friendlier version of a ISO 8601 timestamp.

        Args:
            dt (datetime_cls): datetime to format

            pathsafe (bool):
                if True, uses only path safe characters, otherwise
                adds extra delimiters for better readability

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> import kwutil
            >>> self = kwutil.datetime(2020, 1, 1)
            >>> print(self.isoformat())
            >>> print(self.isoformat(pathsafe=True))
            >>> print(self.ensure_timezone().isoformat())
            >>> print(self.ensure_timezone().isoformat(pathsafe=True))
            2020-01-01T00:00:00
            20200101T000000
            2020-01-01T00:00:00+00:00
            20200101T000000Z
        """
        if pathsafe:
            return _pathsafe_datetime_isoformat(self, sep=sep,
                                                timespec=timespec)
        else:
            return super().isoformat(sep=sep, timespec=timespec)

    def ensure_timezone(dt, default='utc'):
        """
        Gives a datetime object a timezone (utc by default) if it doesnt have one

        Arguments:
            dt (datetime_mod.datetime): the datetime to fix
            default (str): the timezone to use if it does not have one.

        Returns:
            datetime_mod.datetime

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> from kwutil.util_time import *  # NOQA
            >>> plus5 = datetime_mod.timezone(timedelta(hours=+5))
            >>> dt1 = datetime(2020, 1, 1)
            >>> dt2 = dt1.ensure_timezone('utc')
            >>> dt3 = dt1.ensure_timezone(plus5)
            >>> dt4 = dt1.ensure_timezone('local')
            >>> print(f'dt1={dt1}')
            >>> print(f'dt2={dt2}')
            >>> print(f'dt3={dt3}')
            >>> print(f'dt4={dt4}')
            dt1=2020-01-01T00:00:00
            dt2=2020-01-01T00:00:00+00:00
            dt3=2020-01-01T00:00:00+05:00
            ...
        """
        if dt.tzinfo is not None:
            return dt
        else:
            tzinfo = coerce_timezone(default)
            return dt.replace(tzinfo=tzinfo)


class timedelta(timedelta_cls):
    """
    An enhanced timedelta class representing some duration of time.

    Inherits from and behaves as a superset of the standard library
    :class`datetime.timedelta` class.

    ParentDocs:

        Difference between two datetime values.

        timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

        All arguments are optional and default to 0.
        Arguments may be integers or floats, and may be positive or negative.

    Notable changes are as follows:

    * :func:`kwutil.timedelta.coerce` - a flexible constructor to reduce boilerplate for handling multiple input formats (great for CLI inputs).

    * :func:`kwutil.timedelta.random` - a constructor for generating a random time duration (great for tests!).

    * :func:`kwutil.timedelta.to_pint` - convert to a :mod:`pint` time quantity

    * :func:`kwutil.timedelta.to_pandas` - convert to a :mod:`pandas` time delta

    * :func:`kwutil.timedelta.isoformat` - convert to an ISO 8601 time delta

    * :func:`kwutil.timedelta.format` - a readable representation at some resolution

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> import kwutil
        >>> self = kwutil.timedelta.random()
        >>> print(f'self={self}')
    """
    # __slots__ = '_days', '_seconds', '_microseconds', '_hashcode'

    @classmethod
    def random(cls, rng=None, low=None, high=None):
        """
        Create a random time delta

        Args:
            rng (None | int | Random): None, seed or existing random state.
            low (Number): minimum number of seconds (inclusive)
            high (Number): maximum number of seconds (inclusive)

        Returns:
            Self
        """
        from kwutil.util_random import ensure_rng
        rng = ensure_rng(rng)
        if low is None or high is None:
            max_range = int(timedelta.max.total_seconds() // 100)
            if low is None:
                low = -max_range
            if high is None:
                high = max_range
        seconds = rng.randint(low, high)
        self = cls.coerce(seconds)
        return self

    @classmethod
    def coerce(cls, data, nan_policy='raise', none_policy='raise',
               copy_policy='avoid'):
        """
        Create a timedelta based on reasonable interpretation of the input.

        Implemented "reasonable interpretations" are as follows:

            * None or nan with behavior determined by ``none_policy`` and ``nan_policy``.

            * An existing instance of ``datetime.timedelta`` with behavior determined by ``copy_policy``.

            * An number (integer or float) indicating duration in seconds.

            * A string in the form "{magnitude}{optional_whitespace}{unit}" with a numeric-looking magnitude and a known unit.

            Known units are:
                {'y', 'year', 'years'}, {'d', 'day', 'days'},
                {'w', 'week', 'weeks'}, {'m', 'month', 'months'},
                {'H', 'hour', 'hours'}, {'M', 'min', 'mins', 'minute', 'minutes'},
                {'S', 'sec', 'secs', 'second', 'seconds'}

            * A pint parsable string (if pint is available).

            * A pytimeparse-parseable string (if pytimeparse is available).

        Args:
            data (str | int | float):
                If given as a string, attempt to parse out a time duration.
                Otherwise, interpret pure magnitudes in seconds.

            none_policy (str):
                Can be: 'return-None', 'return-nan', or 'raise'.
                See :func:`_handle_null_policy` for details.

            nan_policy (str):
                Can be: 'return-None', 'return-nan', or 'raise'.
                See :func:`_handle_null_policy` for details.

            copy_policy (str): can be 'avoid' or 'always'

        Returns:
            Self | float | None

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> from kwutil.util_time import *  # NOQA
            >>> data = '3.141592653589793 years'
            >>> cls = timedelta
            >>> self = cls.coerce(data)
            >>> print('self = {}'.format(ub.urepr(self, nl=1)))
        """
        self = _coerce_timedelta(data, nan_policy=nan_policy,
                                 none_policy=none_policy, timedelta_cls=cls)
        return self

    def to(self, what):
        """
        Generic conversion to a different format or data structure.

        Args:
            what (str):
                Can be "iso", "pint", "pandas", or it can be a pint
                unit to convert to.

        SeeAlso:
            :func:`timedelta.format` - a direct to-string formatting

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> # xdoctest: +REQUIRES(module:pandas)
            >>> import kwutil
            >>> self = kwutil.timedelta.random(low=0, high=10000, rng=1)
            >>> print(self.to('pandas'))
            >>> print(self.to('iso'))
            >>> print(self.to('pint'))
            >>> print(round(self.to('days'), 2))
            >>> print(round(self.to('microseconds')))
            0 days 00:36:41
            P0DT0H36M41S
            2201.0 second
            0.03 day
            2201000000.0 microsecond
        """
        if what == 'pandas':
            return self.to_pandas()
        elif what == 'pint':
            return self.to_pint()
        elif what == 'iso':
            return self.isoformat()
        else:
            # Assume a pint unit
            return self.to_pint().to(what)

    def to_pint(self):
        """
        Convert the time delta to a pint-based representation of duration

        Returns:
            pint.util.Quantity

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> import kwutil
            >>> self = kwutil.timedelta.random()
            >>> quantity = self.to_pint()
        """
        ureg = _time_unit_registery()
        quantity = self.total_seconds() * ureg.seconds
        return quantity

    def to_pandas(self):
        """
        Returns:
            pd.Timedelta
        """
        import pandas as pd
        return pd.Timedelta(self)

    def isoformat(self):
        """
        ISO 8601 time deltas.

        Format is ``P[n]Y[n]M[n]DT[n]H[n]M[n]S``

        Returns:
            str

        References:
            https://en.wikipedia.org/wiki/ISO_8601#Durations.
        """
        # TODO: should probably do this without pandas
        return self.to_pandas().isoformat()

    def format(self, resolution=None, unit=None, precision=None):
        """
        Format time deltas at some resolution granularity for human readability

        Args:
            delta (datetime_mod.timedelta): The timedelta to format

            unit (str | None | pint.Unit):
                if specified, express the time delta in terms of this unit.

            precision (int):
                number of decimal places when a single unit is given

            resolution (datetime_mod.timedelta | str | None):
                minimum temporal resolution. If unspecified returns
                an isoformat

        Returns:
            str: formatted text

        SeeAlso:
            :func:`timedelta.to` - python format conversion

        References:
            https://gist.github.com/thatalextaylor/7408395
            https://en.wikipedia.org/wiki/ISO_8601#Durations

        Example:
            >>> # xdoctest: +REQUIRES(module:pint)
            >>> from kwutil.util_time import *  # NOQA
            >>> resolution = timedelta.coerce('year')
            >>> resolution = 'year'
            >>> delta = timedelta.coerce('13months')
            >>> print(delta.format())
            >>> print(delta.format(unit='year', precision=2))
            >>> print(timedelta.coerce('.000003 days').format(unit='auto', precision=0))
            >>> print(timedelta.coerce('.03 days').format(unit='auto', precision=0))
            >>> print(timedelta.coerce('39 days').format(unit='auto', precision=0))
            >>> print(timedelta.coerce('3900 days').format(unit='auto', precision=0))
        """
        return _format_timedelta(self, resolution=resolution, unit=unit,
                                 precision=precision)


def coerce_timezone(tz):
    """
    Converts input to a valid timezone object

    Args:
        tz (str | tzinfo): a special code or existing object

    Returns:
        tzinfo: timezone object
    """
    # TODO: use pytz?
    if isinstance(tz, datetime_mod.timezone):
        tzinfo = tz
    elif isinstance(tz, datetime_mod.tzinfo):
        tzinfo = tz
    else:
        if tz == 'utc':
            tzinfo = datetime_mod.timezone.utc
        elif tz == 'local':
            import time
            tzinfo = datetime_mod.timezone(datetime_mod.timedelta(seconds=-time.timezone))
        else:
            raise NotImplementedError(f'Unknown Timezone: {tz!r}')
    return tzinfo


def _format_timedelta(delta, resolution=None, unit=None, precision=None):
    """
    Format time deltas at some resolution granularity

    WORK IN PROGRESS

    Args:
        delta (datetime_mod.timedelta): The timedelta to format

        unit (str | None | pint.Unit):
            if specified, express the time delta in terms of this unit.

        precision (int):
            number of decimal places when a single unit is given

        resolution (datetime_mod.timedelta | str | None):
            minimum temporal resolution. If unspecified returns
            an isoformat

    Returns:
        str: formatted text

    References:
        https://gist.github.com/thatalextaylor/7408395
        https://en.wikipedia.org/wiki/ISO_8601#Durations

    CommandLine:
        xdoctest -m kwutil.util_time format_timedelta

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> from kwutil.util_time import *  # NOQA
        >>> resolution = timedelta.coerce('year')
        >>> resolution = 'year'
        >>> delta = timedelta.coerce('13months')
        >>> print(format_timedelta(delta))
        >>> print(format_timedelta(delta, unit='year', precision=2))

        >>> print(format_timedelta('.000003 days', unit='auto', precision=0))
        >>> print(format_timedelta('.03 days', unit='auto', precision=0))
        >>> print(format_timedelta('39 days', unit='auto', precision=0))
        >>> print(format_timedelta('3900 days', unit='auto', precision=0))
    """
    if resolution is None and unit is None:
        return str(delta)
    else:
        ureg = _time_unit_registery()
        delta = timedelta.coerce(delta)
        delta_sec = delta.total_seconds()

        unitkw = {}
        if isinstance(unit, dict):
            # Hack to allow more control over "auto" behavior without adding
            # new params. May want to redesign api later.
            unitkw = unit
            if 'value' in unit:
                unit = unit['value']
            else:
                raise NotImplementedError

        if unit == 'auto':
            # Figure out the "best" unit to express the delta in
            seconds = int(delta_sec)
            years, seconds = divmod(seconds, 31536000)
            week, seconds = divmod(seconds, 604800)
            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)

            min_unit = unitkw.get('min_unit', 'sec')
            exclude_units = set(unitkw.get('exclude_units', []))
            # todo: max_unit = unitkw.get('max_unit', 'sec')

            # TODO: ms, us, ns
            unit_order = [('year', years),
                          ('week', week),
                          ('day', days),
                          ('hour', hours),
                          ('min', minutes),
                          ('sec', seconds)]

            for cand_text, value in unit_order:
                if cand_text in exclude_units:
                    continue
                if value > 0:
                    unit = cand_text
                    break
                if min_unit == cand_text:
                    unit = min_unit
                    break

            # if years > 0:
            #     unit = 'year'
            # elif week > 0:
            #     unit = 'week'
            # elif days > 0:
            #     unit = 'day'
            # elif hours > 0:
            #     unit = 'hour'
            # elif minutes > 0:
            #     unit = 'min'
            # else:
            #     unit = 'sec'
            #     # TODO: ms, us, ns

        if isinstance(unit, str):
            unit = ureg.parse_units(unit)
        elif isinstance(unit, ureg.Unit):
            ...
        else:
            raise TypeError(type(unit))

        if unit is not None:
            pint_sec = delta_sec * ureg.sec
            new_unit = pint_sec.to(unit)
            text = ub.urepr(new_unit, precision=precision)
            return text

        raise NotImplementedError


def _pathsafe_datetime_isoformat(dt, sep='T', timespec='seconds'):
    date_fmt = '%Y%m%d'
    if timespec == 'seconds':
        time_tmf = '%H%M%S'
    else:
        raise NotImplementedError(timespec)

    text = dt.strftime(''.join([date_fmt, sep, time_tmf]))
    if dt.tzinfo is not None:
        off = dt.utcoffset()
        off_seconds = off.total_seconds()
        if off_seconds == 0:
            # TODO: use codes for offsets to remove the plus sign if possible
            suffix = 'Z'
        elif off_seconds % 3600 == 0:
            tz_hour = int(off_seconds // 3600)
            suffix = '{:02d}'.format(tz_hour) if tz_hour < 0 else '+{:02d}'.format(tz_hour)
        else:
            suffix = _format_offset(off)
        text += suffix
    return text


def _datetime_isoformat(dt, sep='T', timespec='seconds', pathsafe=True):
    """
    A path-safe version of datetime_cls.isotime() that returns a
    path-friendlier version of a ISO 8601 timestamp.

    Args:
        dt (datetime_cls): datetime to format

        pathsafe (bool):
            if True, uses only path safe characters, otherwise
            adds extra delimiters for better readability

    References:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    SeeAlso:
        :func:`ubelt.timestamp`

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> from kwutil.util_time import *  # NOQA
        >>> items = []
        >>> dt = datetime_mod.datetime.now()
        >>> dt = ensure_timezone(dt, datetime_mod.timezone(datetime_mod.timedelta(hours=+5)))
        >>> items.append(dt)
        >>> dt = datetime_mod.datetime.utcnow()
        >>> items.append(dt)
        >>> dt = dt.replace(tzinfo=datetime_mod.timezone.utc)
        >>> items.append(dt)
        >>> dt = ensure_timezone(datetime_mod.datetime.now(), datetime_mod.timezone(datetime_mod.timedelta(hours=-5)))
        >>> items.append(dt)
        >>> dt = ensure_timezone(datetime_mod.datetime.now(), datetime_mod.timezone(datetime_mod.timedelta(hours=+5)))
        >>> items.append(dt)
        >>> print('items = {!r}'.format(items))
        >>> for dt in items:
        >>>     print('----')
        >>>     print('dt = {!r}'.format(dt))
        >>>     # ISO format is cool, but it doesnt give much control
        >>>     print(dt.isoformat())
        >>>     # Our extension has better flexibility
        >>>     print(isoformat(dt))
        >>>     print(isoformat(dt, pathsafe=False))
    """
    if not pathsafe:
        return dt.isoformat(sep=sep, timespec=timespec)
    return _pathsafe_datetime_isoformat(dt, sep=sep, timespec=timespec)


def _format_offset(off):
    """
    Taken from CPython:
        https://github.com/python/cpython/blob/main/Lib/datetime_mod.py
    """
    s = ''
    if off is not None:
        if off.days < 0:
            sign = "-"
            off = -off
        else:
            sign = "+"
        hh, mm = divmod(off, datetime_mod.timedelta(hours=1))
        mm, ss = divmod(mm, datetime_mod.timedelta(minutes=1))
        s += "%s%02d:%02d" % (sign, hh, mm)
        if ss or ss.microseconds:
            s += ":%02d" % ss.seconds

            if ss.microseconds:
                s += '.%06d' % ss.microseconds
    return s


def _try_copy_dt_to_cls(cls, dt):
    try:
        dt = cls(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                 dt.second, dt.microsecond, dt.tzinfo)
    except TypeError:
        # let pandas.NaT pass through
        if math.isnan(dt.total_seconds()):
            ...
        else:
            raise
    except AttributeError:
        ...
    except Exception as ex:
        from kwutil import util_exception
        raise util_exception.add_exception_note(ex, ub.paragraph(
            f'''
            Issue copying datetime class with dt={dt}, cls={cls}.
            And:
            year={dt.year},
            month={dt.month},
            day={dt.day},
            hour={dt.hour},
            minute={dt.minute},
            second={dt.second},
            microsecond={dt.microsecond},
            tzinfo={dt.tzinfo},
            '''))
    return dt


@profile
def _coerce_datetime(data, default_timezone='utc', nan_policy='return-None',
                     none_policy='return-None', copy_policy='avoid', cls=None):
    """
    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> from kwutil.util_time import *  # NOQA
        >>> assert coerce_datetime(None) is None
        >>> assert coerce_datetime(float('nan')) is None
        >>> assert coerce_datetime('2020-01-01') == datetime_cls(2020, 1, 1, 0, 0, tzinfo=datetime_mod.timezone.utc)
        >>> assert coerce_datetime(datetime_cls(2020, 1, 1, 0, 0)) == datetime_cls(2020, 1, 1, 0, 0, tzinfo=datetime_mod.timezone.utc)
        >>> assert coerce_datetime(datetime_cls(2020, 1, 1, 0, 0).date()) == datetime_cls(2020, 1, 1, 0, 0, tzinfo=datetime_mod.timezone.utc)
        >>> dt = coerce_datetime('2020-01-01')
        >>> stamp = dt.timestamp()
        >>> assert stamp == 1577836800.0
        >>> assert coerce_datetime(stamp) == dt
        >>> assert dt.isoformat() == '2020-01-01T00:00:00+00:00'
    """
    try:
        from dateutil import parser as date_parser
    except ImportError:
        warnings.warn('warning: kwutil.util_time._coerce_datetime requires python_dateutil, but it is not installed')
        raise
    if cls is None:
        cls = datetime_mod.datetime

    if data is None:
        return _handle_null_policy(
            none_policy, TimeTypeError,
            'cannot coerce None to a datetime when '
            f'none_policy={none_policy!r}.')
    elif isinstance(data, str):
        # Canse use ubelt.timeparse(data, default_timezone=default_timezone) here.
        if data == 'now':
            dt = cls.utcnow()
        else:
            # Note: this is a fairly slow call.
            dt = date_parser.parse(data)
            try:
                dt = cls(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                         dt.second, dt.microsecond, dt.tzinfo)
            except AttributeError:
                ...
    elif isinstance(data, datetime_cls):
        dt = data
        if copy_policy == 'avoid':
            if not isinstance(dt, cls):
                dt = _try_copy_dt_to_cls(cls, dt)
        else:
            raise KeyError(copy_policy)
    elif isinstance(data, datetime_mod.date):
        dt = date_parser.parse(data.isoformat())
        dt = _try_copy_dt_to_cls(cls, dt)
    elif isinstance(data, numbers.Number):
        if math.isnan(data):
            return _handle_null_policy(
                nan_policy, TimeTypeError,
                'cannot coerce nan to a datetime when '
                f'nan_policy={nan_policy!r}.')

        tz = coerce_timezone(default_timezone)
        dt = cls.fromtimestamp(data, tz=tz)
        # OLD INCORRECT IMPLEMENTATION:
        # dt = datetime_cls.fromtimestamp(data)
    else:
        raise TimeTypeError('unhandled {}'.format(data))
    dt = _ensure_timezone(dt, default=default_timezone)
    return dt


def _handle_null_policy(policy, ex_type=TypeError,
                        ex_msg='cannot accept null input'):
    """
    For handling a nan or None policy.

    Args:
        policy (str):
            How null inputs are handled. Can be:
                'return-None': returns None
                'return-nan': returns nan
                'raise': raises an error

        ex_type (type): Exception type to raise if policy is raise

        ex_msg (msg): Exception arguments
    """
    if policy == 'return-None':
        return None
    elif policy == 'return-nan':
        return float('nan')
    elif policy == 'raise':
        raise ex_type(ex_msg)
    else:
        raise KeyError(ub.paragraph(
            f'''
            Unknown null policy={policy!r}.
            Valid choices are "return-None", "return-nan", and "raise".
            '''))


@profile
def _coerce_timedelta(delta, nan_policy='raise', none_policy='raise',
                      copy_policy='avoid', timedelta_cls=None):
    """
    Parses data that could be associated with a time delta.

    Backend for timedelta.coerce

    Args:
        delta (str | int | float):
            If given as a string, attempt to parse out a time duration.
            Otherwise, interpret pure magnitudes in seconds.

        none_policy (str):
            Can be: 'return-None', 'return-nan', or 'raise'.
            See :func:`_handle_null_policy` for details.

        nan_policy (str):
            Can be: 'return-None', 'return-nan', or 'raise'.
            See :func:`_handle_null_policy` for details.

        copy_policy (str): can be 'avoid' or 'always'

    Returns:
        datetime_mod.timedelta | None

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> # xdoctest: +REQUIRES(module:pytimeparse)
        >>> from kwutil.util_time import *  # NOQA
        >>> variants = [
        >>>     ['year', 'y'],
        >>>     ['month', 'm', 'mon'],
        >>>     ['day', 'd', 'days'],
        >>>     ['hours', 'hour', 'h'],
        >>>     ['minutes', 'min', 'M'],
        >>>     ['second', 'S', 's', 'secs'],
        >>> ]
        >>> for vs in variants:
        >>>     print('vs = {!r}'.format(vs))
        >>>     ds = []
        >>>     for v in vs:
        >>>         d = timedelta.coerce(f'1{v}')
        >>>         ds.append(d)
        >>>         d = timedelta.coerce(f'1 {v}')
        >>>         ds.append(d)
        >>>     assert ub.allsame(ds)
        >>>     print('ds = {!r}'.format(ds))
        >>> print(timedelta.coerce(10.3))
        >>> print(timedelta.coerce('1y'))
        >>> print(timedelta.coerce('1m'))
        >>> print(timedelta.coerce('1d'))
        >>> print(timedelta.coerce('1H'))
        >>> print(timedelta.coerce('1M'))
        >>> print(timedelta.coerce('1S'))
        >>> print(timedelta.coerce('1year'))
        >>> print(timedelta.coerce('1month'))
        >>> print(timedelta.coerce('1day'))
        >>> print(timedelta.coerce('1hour'))
        >>> print(timedelta.coerce('1min'))
        >>> print(timedelta.coerce('1sec'))
        >>> print(timedelta.coerce('1microsecond'))
        >>> print(timedelta.coerce('1milliseconds'))
        >>> print(timedelta.coerce('1ms'))
        >>> print(timedelta.coerce('1us'))

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> # xdoctest: +REQUIRES(module:numpy)
        >>> from kwutil.util_time import *  # NOQA
        >>> import numpy as np
        >>> print(timedelta.coerce(int(30)))
        >>> print(timedelta.coerce(float(30)))
        >>> print(timedelta.coerce(np.int32(30)))
        >>> print(timedelta.coerce(np.int64(30)))
        >>> print(timedelta.coerce(np.float32(30)))
        >>> print(timedelta.coerce(np.float64(30)))

    References:
        https://docs.python.org/3.4/library/datetime_mod.html#strftime-strptime-behavior
    """
    if isinstance(delta, str):
        try:
            delta = float(delta)
        except ValueError:
            ...

    if timedelta_cls is None:
        timedelta_cls = datetime_mod.timedelta

    if isinstance(delta, datetime_mod.timedelta):
        if copy_policy == 'avoid':
            if not isinstance(delta, timedelta_cls):
                delta = timedelta_cls(seconds=delta.total_seconds())
        elif copy_policy == 'always':
            delta = timedelta_cls(seconds=delta.total_seconds())
        else:
            raise KeyError(copy_policy)
    elif isinstance(delta, numbers.Number):
        try:
            delta = timedelta_cls(seconds=delta)
        except TypeError:
            import sys
            np = sys.modules.get('numpy', None)
            if np is None:
                raise
            else:
                if isinstance(delta, np.integer):
                    delta = timedelta_cls(seconds=int(delta))
                elif isinstance(delta, np.floating):
                    delta = timedelta_cls(seconds=float(delta))
                else:
                    raise
        except ValueError:
            if isinstance(delta, float) and math.isnan(delta):
                return _handle_null_policy(
                    nan_policy, TimeTypeError,
                    'cannot coerce nan to a timedelta when '
                    f'nan_policy={nan_policy!r}')
            raise
    elif isinstance(delta, str):
        # TODO: handle isoformat
        try:
            # Note: this breaks for '4 days 10:10:21'
            ureg = _time_unit_registery()
            parsed = ureg.parse_expression(delta)
            seconds = parsed.to('seconds').m
            # timedelta apparently does not have resolution higher than
            # microseconds.
            # https://stackoverflow.com/questions/10611328/strings-ns
            # https://bugs.python.org/issue15443
            delta = timedelta_cls(seconds=seconds)
        except Exception:
            # Separate the expression into a magnitude and a unit
            import re
            expr_pat = re.compile(
                r'^(?P<magnitude>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)'
                '(?P<spaces> *)'
                '(?P<unit>.*)$')
            match = expr_pat.match(delta.strip())
            if match:
                parsed = match.groupdict()
                unit = parsed.get('unit', '')
                magnitude = parsed.get('magnitude', '')
            else:
                unit = None
                magnitude = None

            if unit in {'y', 'year', 'years'}:
                delta = timedelta_cls(days=365 * float(magnitude))
            elif unit in {'d', 'day', 'days'}:
                delta = timedelta_cls(days=1 * float(magnitude))
            elif unit in {'w', 'week', 'weeks'}:
                delta = timedelta_cls(days=7 * float(magnitude))
            elif unit == {'m', 'month', 'months'}:
                delta = timedelta_cls(days=30.437 * float(magnitude))
            elif unit == {'H', 'hour', 'hours'}:
                delta = timedelta_cls(hours=float(magnitude))
            elif unit == {'M', 'min', 'mins', 'minute', 'minutes'}:
                delta = timedelta_cls(minutes=float(magnitude))
            elif unit == {'S', 'sec', 'secs', 'second', 'seconds'}:
                delta = timedelta_cls(seconds=float(magnitude))
            else:
                try:
                    import pytimeparse  #
                except ImportError:
                    warnings.warn('warning: pytimeparse is not available, but needed by kwutil.util_time._coerce_timedelta')
                    raise
                else:
                    warnings.warn('warning: pytimeparse fallback')
                    seconds = pytimeparse.parse(delta)
                    if seconds is None:
                        raise Exception(delta)
                    delta = timedelta_cls(seconds=seconds)
                    return delta
    else:
        if delta is None:
            return _handle_null_policy(
                none_policy, TimeTypeError,
                'cannot coerce None to a timedelta when'
                f'none_policy={none_policy!r}'
            )
        raise TimeTypeError(f'cannot coerce {type(delta)} to a timedelta')
    return delta


def _ensure_timezone(dt, default='utc'):
    """
    Gives a datetime object a timezone (utc by default) if it doesnt have one

    Arguments:
        dt (datetime_mod.datetime): the datetime to fix
        default (str): the timezone to use if it does not have one.

    Returns:
        datetime_mod.datetime

    Example:
        >>> # xdoctest: +REQUIRES(module:pint)
        >>> from kwutil.util_time import *  # NOQA
        >>> dt = ensure_timezone(datetime_cls.now(), datetime_mod.timezone(datetime_mod.timedelta(hours=+5)))
        >>> print('dt = {!r}'.format(dt))
        >>> dt = ensure_timezone(datetime_cls.utcnow())
        >>> print('dt = {!r}'.format(dt))
        >>> ensure_timezone(datetime_cls.utcnow(), 'utc')
        >>> ensure_timezone(datetime_cls.utcnow(), 'local')
    """
    if dt.tzinfo is not None:
        return dt
    else:
        tzinfo = coerce_timezone(default)
        return dt.replace(tzinfo=tzinfo)


@cache
def _time_unit_registery():
    """
    TODO: use kwutil.util_units?
    """
    import sys
    if sys.version_info[0:2] == (3, 9):
        # backwards compatibility support for numpy 2.0 and pint on cp39
        try:
            import numpy as np
        except ImportError:
            ...
        else:
            if not np.__version__.startswith('1.'):
                np.cumproduct = np.cumprod

    import pint
    # Empty registry
    ureg = pint.UnitRegistry(None)
    ureg.define('second = []')
    ureg.define('minute = 60 * second')
    ureg.define('hour = 60 * minute')

    ureg.define('day = 24 * hour')
    ureg.define('week = 7 * day')
    ureg.define('month = 30.437 * day')
    ureg.define('year = 365 * day')

    ureg.define('min = minute')
    ureg.define('mon = month')
    ureg.define('sec = second')

    ureg.define('S = second')
    ureg.define('M = minute')
    ureg.define('H = hour')

    ureg.define('d = day')
    ureg.define('m = month')
    ureg.define('y = year')

    ureg.define('s = second')

    ureg.define('millisecond = second / 1000')
    ureg.define('microsecond = second / 1000000')

    ureg.define('ms = millisecond')
    ureg.define('us = microsecond')

    @ub.urepr.extensions.register(pint.Unit)
    def format_unit(data, **kwargs):
        numer = [k for k, v in data._units.items() if v > 0]
        denom = [k for k, v in data._units.items() if v < 0]
        numer_str = ' '.join(numer)
        if len(denom) == 0:
            return numer_str
        elif len(denom) > 1:
            denom_str = '({})'.format(' '.join(denom))
        elif len(denom) == 1:
            denom_str = ' '.join(denom)
        else:
            raise AssertionError
        if len(numer) == 0:
            return '/ ' + denom_str
        else:
            return numer_str + ' / ' + denom_str

    @ub.urepr.extensions.register(pint.Quantity)
    def format_quantity(data, _return_info=None, **kwargs):
        mag_repr = ub.urepr(data.magnitude, **kwargs)
        unit_repr = ub.urepr(data.u)
        return  mag_repr + ' ' + unit_repr

    return ureg

_time_unit_registery()


def _devcheck_portion():
    """
    Portion seems like a good library to build a TimeInterval class with.
    Could also check PyInterval. Arrow also seems to have interval support,
    maybe just integrate with that?
    """
    import kwutil
    import portion
    delta = abs(kwutil.util_time.timedelta.coerce('1 year'))
    start = kwutil.util_time.datetime.coerce('2020-01-01')
    interval1 = portion.Interval.from_atomic(portion.CLOSED, start, start + delta, portion.CLOSED)
    interval2 = portion.Interval.from_atomic(portion.CLOSED, start + delta * 0.5, start + delta * 1.5, portion.CLOSED)
    interval3 = portion.Interval.from_atomic(portion.CLOSED, start + delta * 3, start + delta * 4, portion.CLOSED)

    interval1 & interval2
    interval1 & interval3
    interval1 | interval3
    interval1 | interval2
    print(f'interval1={interval1}')
    print(f'interval2={interval2}')
    print(f'interval3={interval3}')
    # See Also:
    # https://pyinterval.readthedocs.io/en/latest/api.html#interval-interval-arithmetic

# Backwards compat, use timedelta.coerce instead
coerce_timedelta = _coerce_timedelta
coerce_datetime = _coerce_datetime
isoformat = _datetime_isoformat
ensure_timezone = _ensure_timezone
format_timedelta = _format_timedelta
