"""
A instance-oriented API into the stdlib logging module, and may eventually
support different backends (e.g. picologging).
"""
import logging
from logging import (
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
)
from abc import ABC, abstractmethod
import sys

__all__ = ["Logger", "LoggerMixin"]


class _LogBackend(ABC):
    """
    Abstract base class for our logger implementations.
    """

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def debug(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def critical(self, msg, *args, **kwargs):
        pass


class _PrintLogBackend(_LogBackend):
    """
    A simple print-based logger that falls back to print output if no logging configuration
    is set up.

    Example:
        >>> from kwutil.util_logging import *  # NOQA
        >>> pl = _PrintLogBackend(name='print', level=INFO)
        >>> pl.info('Hello %s', 'world')
        Hello world
        >>> pl.debug('Should not appear')
    """

    def __init__(self, name="<print-logger>", level=INFO):
        super().__init__(name)
        self.level = level

    def isEnabledFor(self, level):
        return level >= self.level

    def _log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            # Mimic logging formatting (ignoring extra kwargs for simplicity)
            print(msg % args)

    def debug(self, msg, *args, **kwargs):
        self._log(DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(CRITICAL, msg, *args, **kwargs)

    def configure(self, **kwargs):
        """
        For compatability with _StdlibLogBackend, all arguments are ignored.
        The print backend does not need to be configured.
        """
        ...


class _LoguruLogBackend(_LogBackend):
    """
    EXPERIMENTAL, loguru might break the paradigmns we have here.

    A loguru-based backend that mimics the same interface as the stdlib and print backends.

    Example:
        >>> # xdoctest: +REQUIRES(module:loguru)
        >>> from kwutil.util_logging import _LoguruLogBackend
        >>> self = _LoguruLogBackend("loguru-test")
        >>> self.info('does not print')
        >>> self.configure(level="INFO")
        >>> self.debug("DEBUG Hello %s", "world")
        >>> self.info("Hello %s", "world")
        >>> self.configure(level="DEBUG")
        >>> self.debug("DEBUG Hello %s", "world")
        >>> self.info("Hello %s", "world")
    """

    def __init__(self, name="<loguru>"):
        super().__init__(name)
        try:
            import loguru  # NOQA
        except ImportError as e:
            raise ImportError("loguru must be installed to use the loguru backend") from e
        # from loguru import logger as _logger
        from loguru._logger import Logger as _Logger
        from loguru._logger import Core as _Core
        # This is an independent loguru instance that doesn't auto-init
        logger = _Logger(
            core=_Core(),
            exception=None,
            depth=0,
            record=False,
            lazy=False,
            colors=False,
            raw=False,
            capture=True,
            patchers=[],
            extra={},
        )
        self.logger = logger
        self.logger.disable(name)
        self._handler_ids = []

    def configure(self, level="INFO", file=None, stream=True, format=None, **kwargs):
        """
        Configure loguru logger.

        Args:
            level (str | int): log level string or int
            file (str | dict | None): path or dict with options for loguru.add
            stream (bool | dict): whether to add stdout handler (or dict config)
            format (str | None): log format
        """
        # Remove any previously added handlers to avoid duplicates
        for handler_id in self._handler_ids:
            self.logger.remove(handler_id)
        self._handler_ids.clear()

        default_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        used_format = format or default_format

        if stream:
            stream_kwargs = stream if isinstance(stream, dict) else {}
            handler_id = self.logger.add(
                sys.stdout,
                level=level,
                format=stream_kwargs.get("format", used_format),
                **{k: v for k, v in stream_kwargs.items() if k != "format"},
            )
            self._handler_ids.append(handler_id)

        if file:
            if isinstance(file, dict):
                filepath = file.get("path")
                if filepath:
                    handler_id = self.logger.add(
                        filepath,
                        level=level,
                        format=file.get("format", used_format),
                        rotation=file.get("rotation", None),
                        compression=file.get("compression", None),
                    )
                    self._handler_ids.append(handler_id)
            else:
                handler_id = self.logger.add(file, level=level, format=used_format)
                self._handler_ids.append(handler_id)

        return self

    def debug(self, msg, *args, **kwargs):
        self.logger.opt(depth=1).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.opt(depth=1).info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.opt(depth=1).warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.opt(depth=1).error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.opt(depth=1).critical(msg, *args, **kwargs)


class _StdlibLogBackend(_LogBackend):
    """
    A wrapper for Python's standard logging.Logger.

    The constructor optionally adds a StreamHandler (to stdout) and/or a logging.FileHandler if file is specified.

    Example:
        >>> from kwutil.util_logging import *  # NOQA
        >>> from kwutil.util_logging import _StdlibLogBackend
        >>> import os
        >>> import ubelt as ub
        >>> import logging
        >>> dpath = ub.Path.appdir('kwutil/test/logging').ensuredir()
        >>> fpath = (dpath / 'test.log').delete()
        >>> sl = _StdlibLogBackend('stdlib')
        >>> sl.info('This wont print')
        >>> sl.configure(
        >>>     level=logging.INFO,
        >>>     stream={
        >>>         'format': '%(asctime)s : [stream] %(levelname)s : %(message)s',
        >>>     },
        >>>     file={
        >>>         'path': fpath,
        >>>         'format': '%(asctime)s : [file] %(levelname)s : %(message)s',
        >>>     }
        >>> )
        >>> sl.info('Hello %s', 'world')
        >>> # Check that the log file has been written to
        >>> text = fpath.read_text()
        >>> print(text)
        >>> assert text.strip().endswith('Hello world')
    """

    def __init__(self, name):
        super().__init__(name)
        self.logger = logging.getLogger(name)

    def _configure_from_dict(self, config_dict):
        """
        Configure the logger using a standard logging.config.dictConfig dictionary.

        Args:
            config_dict (dict): The dictionary used for configuring logging.
        """
        logging.config.dictConfig(config_dict)
        self.logger = logging.getLogger(self.name)
        return self

    def _configure_from_file(self, path):
        """
        Configure the logger using a standard logging config file.

        Args:
            path (str): The path to the config file (ini format).
        """
        logging.config.fileConfig(path, disable_existing_loggers=False)
        self.logger = logging.getLogger(self.name)
        return self

    def configure(
        self,
        level=None,
        stream='auto',
        file=None,
    ):
        """
        Configure the underlying stdlib logger.

        Parameters:
            level: the logging level to set (e.g. logging.INFO)
            stream: either a dict with configuration or a boolean/'auto'
                - If dict, expected keys include 'format'
                - If 'auto', the stream handler is enabled if no handlers are set
                - If a boolean, True enables the stream handler.
            file: either a dict with configuration or a path string.
                - If dict, expected keys include 'path' and 'format'
                - If a string, it is taken as the file path


        Note:
            For special attributes for the ``format`` argument of ``stream``
            and ``file`` see
            https://docs.python.org/3/library/logging.html#logrecord-attributes

        Returns:
            self (the configured _StdlibLogBackend instance)
        """
        if level is not None:
            self.logger.setLevel(level)

        # Default settings for file and stream handlers
        fileinfo = {
            'path': None,
            'format': '%(asctime)s : [file] %(levelname)s : %(message)s'
        }
        streaminfo = {
            '__enable__': None,  # will be determined below
            'format': '%(levelname)s: %(message)s',
        }

        # Update stream info if stream is a dict
        if isinstance(stream, dict):
            streaminfo.update(stream)
            # If not specified otherwise, enable the stream handler.
            if streaminfo.get('__enable__') is None:
                streaminfo['__enable__'] = True
        else:
            # If stream is not a dict, treat it as a boolean or 'auto'
            streaminfo['__enable__'] = stream

        # If stream is 'auto', enable stream only if no handlers are present.
        if streaminfo['__enable__'] == 'auto':
            streaminfo['__enable__'] = not bool(self.logger.handlers)

        # Update file info if file is a dict
        if isinstance(file, dict):
            fileinfo.update(file)
        else:
            fileinfo['path'] = file

        # Add a stream handler if enabled
        if streaminfo['__enable__']:
            streamformat = streaminfo.get('format')
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(logging.Formatter(streamformat))
            self.logger.addHandler(sh)

        # Add a file handler if a valid path is provided
        path = fileinfo.get('path')
        if path:
            fileformat = fileinfo.get('format')
            fh = logging.FileHandler(path)
            fh.setFormatter(logging.Formatter(fileformat))
            self.logger.addHandler(fh)

        return self

    # def _setup_handlers(self, stream, file):
    #     # Only add handlers if none exist, so as not to duplicate logs.
    #     if not self.logger.handlers:

    def debug(self, msg, *args, **kwargs):
        kwargs['stacklevel'] = kwargs.get('stacklevel', 1) + 1
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        kwargs['stacklevel'] = kwargs.get('stacklevel', 1) + 1
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        kwargs['stacklevel'] = kwargs.get('stacklevel', 1) + 1
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        kwargs['stacklevel'] = kwargs.get('stacklevel', 1) + 1
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs['stacklevel'] = kwargs.get('stacklevel', 1) + 1
        self.logger.critical(msg, *args, **kwargs)


class Logger:
    """
    The main Logger class that automatically selects the backend.

    If backend='auto' and a global logging configuration exists (i.e. logging.getLogger(name) has handlers),
    it uses _StdlibLogBackend; otherwise, it falls back to _PrintLogBackend.

    Optional parameters:
      - verbose: controls log level via an integer (0: CRITICAL, 1: INFO, 2: DEBUG, etc.)
      - file: if provided, file logging is enabled (only used with _StdlibLogBackend)
      - stream: if True, a logging.StreamHandler to stdout is added (only used with _StdlibLogBackend)

    Example:
        >>> # With no global handlers, defaults to _PrintLogBackend
        >>> from kwutil.util_logging import *  # NOQA
        >>> logger = Logger('TestLogger', verbose=2, backend='auto')
        >>> logger.info('Hello %s', 'world')
        Hello world
        >>> # Forcing use of _PrintLogBackend
        >>> logger = Logger('TestLogger', verbose=2, backend='print')
        >>> logger.debug('Debug %d', 123)
        Debug 123
        >>> # Forcing use of Stdlib Logger
        >>> logger = Logger('TestLogger', verbose=2, backend='stdlib')
        >>> logger.debug('Debug %d', 123)

    Example:
        >>> # Forcing use of Stdlib Logger
        >>> from kwutil.util_logging import *  # NOQA
        >>> logger = Logger('TestLogger', verbose=2, backend='stdlib').configure(
        >>>     stream={'format': '%(asctime)s : %(pathname)s:%(lineno)d %(funcName)s  %(levelname)s : %(message)s'})
        >>> logger.debug('Debug %d', 123)
        >>> logger.info('Hello %d', 123)
    """
    def __init__(self, name="Logger", verbose=1, backend="auto", file=None, stream=True):
        # Map verbose level to logging levels. If verbose > 1, show DEBUG, else INFO.
        level = {0: CRITICAL, 1: INFO, 2: DEBUG}.get(verbose, DEBUG)
        if backend == "auto":
            # Choose _StdlibLogBackend if a logger with handlers exists.
            backend_choice = (
                _StdlibLogBackend(name).configure(level=level, file=file, stream=stream)
                if logging.getLogger(name).handlers
                else _PrintLogBackend(name, level)
            )
        elif backend == "print":
            backend_choice = _PrintLogBackend(name, level)
        elif backend == "stdlib":
            backend_choice = _StdlibLogBackend(name).configure(level, file=file, stream=stream)
        elif backend == "loguru":
            backend_choice = _LoguruLogBackend(name).configure(level=level, file=file, stream=stream)
        else:
            raise ValueError("Unsupported backend. Use 'auto', 'print', 'loguru', or 'stdlib'.")
        self._backend = backend_choice

    def __getattr__(self, attr):
        # We should not need to modify stacklevel here as we are directly
        # returning the backend function and not wrapping it.
        return getattr(self._backend, attr)


class LoggerMixin:
    """
    Mixin that provides an instance-level logger.

    Example:
        >>> from kwutil.util_logging import *  # NOQA
        >>> class MyClass(LoggerMixin):
        ...     def __init__(self, verbose=1, backend='auto'):
        ...         super().__init__(verbose=verbose, backend=backend)
        ...         self.info('Logger initialized for %s', self.__class__.__name__)
        >>> obj = MyClass(verbose=2, backend='print')
        Logger initialized for MyClass
        >>> obj = MyClass(verbose=2, backend='stdlib')
        >>> obj.info('hello')
    """
    def __init__(self, name=None, verbose=1, backend="auto", file=None, stream=True):
        if name is None:
            name = self.__class__.__name__ + str(id(self))
        self.logger = Logger(name, verbose, backend, file=file, stream=stream)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
