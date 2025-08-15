#!/usr/bin/env python3
"""

"""
# mypy: disable-error-code="attr-defined"
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import functools as ftz
import itertools as itz
import logging as logmod
import logging.handlers as l_handlers
import os
import pathlib as pl
import re
import time
import types
import weakref
from sys import stderr, stdout
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 1st party imports
from jgdv import Mixin, Proto
from jgdv._abstract.protocols.general import Buildable_p
from jgdv._abstract.protocols.pydantic import ProtocolModelMeta
from jgdv.structs.chainguard import ChainGuard

# ##-- end 1st party imports

from . import _interface as API # noqa: N812
from .filter import BlacklistFilter, WhitelistFilter
from .format import ColourFormatter, StripColourFormatter

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType, Any
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError
if TYPE_CHECKING:
    import enum
    from jgdv import Maybe, RxStr
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable
    from ._interface import Handler, Formatter

##--|
from jgdv import Maybe
# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

env                  : dict             = cast("dict", os.environ)
IS_PRE_COMMIT        : Final[bool]      = "PRE_COMMIT" in env
DEFAULT_FORMAT       : Final[str] = "{levelname:<8} : {message}"
DEFAULT_FILE_FORMAT  : Final[str] = "%Y-%m-%d::%H:%M.log"
DEFAULT_STYLE : Final[str] = "{"
##--|
class HandlerBuilder_m:
    """
    Loggerspec Mixin for building handlers
    """

    def _build_streamhandler(self) -> Handler:
        return logmod.StreamHandler(stdout)

    def _build_errorhandler(self) -> Handler:
        return logmod.StreamHandler(stderr)

    def _build_filehandler(self, path:pl.Path) -> Handler:
        return logmod.FileHandler(path, mode='w')

    def _build_rotatinghandler(self, path:pl.Path) -> Handler:
        handler = l_handlers.RotatingFileHandler(path, backupCount=API.MAX_FILES)
        handler.doRollover()
        return handler

    def _build_formatter(self, handler:Handler) -> Formatter:
        formatter : Formatter
        match self.colour:
            case _ if IS_PRE_COMMIT:
                # Always strip colour when in pre-commit
                formatter = StripColourFormatter(fmt=self.format, style=self.style)
            case _ if isinstance(handler, logmod.FileHandler|l_handlers.RotatingFileHandler):
                # Always strip colour when logging to a file
                formatter = StripColourFormatter(fmt=self.format, style=self.style)
            case False:
                formatter = StripColourFormatter(fmt=self.format, style=self.style)
            case str() | True:
                formatter = ColourFormatter(fmt=self.format, style=self.style)
                formatter.apply_colour_mapping(API.alt_log_colours)

        return formatter

    def _build_filters(self) -> list[Callable]:
        filters : list[Callable] = []
        if bool(self.allow):
            filters.append(WhitelistFilter(self.allow))
        if bool(self.filter):
            filters.append(BlacklistFilter(self.filter))

        return filters

    def _discriminate_handler(self, target:Maybe[str|pl.Path]) -> tuple[Maybe[Handler], Maybe[Formatter]]:
        handler, formatter = None, None

        match target:
            case "pass" | None:
                return None, None
            case "file":
                log_file_path      = self.logfile()
                handler            = self._build_filehandler(log_file_path)
            case "rotate":
                log_file_path      = self.logfile()
                handler            = self._build_rotatinghandler(log_file_path)
            case "stdout":
                handler   = self._build_streamhandler()
            case "stderr":
                handler = self._build_errorhandler()
            case _:
                msg = "Unknown logger spec target"
                raise ValueError(msg, target)

        formatter = self._build_formatter(handler)

        assert(handler   is not None)
        assert(formatter is not None)
        return handler, formatter

##--|

@Proto(Buildable_p)
class LoggerSpec(HandlerBuilder_m, BaseModel, metaclass=ProtocolModelMeta):
    """
      A Spec for toml defined logging control.
      Allows user to name a logger, set its level, format,
      filters, colour, and what (cli arg) verbosity it activates on,
      and what file it logs to.

      When 'apply' is called, it gets the logger,
      and sets any relevant settings on it.
    """
    ##--| classvars
    RootName                   : ClassVar[str]                   = "root"
    levels                     : ClassVar[type[enum.IntEnum]]    = API.LogLevel_e
    ##--| main
    name                       : str
    disabled                   : bool                            = False
    base                       : Maybe[str]                      = None
    level                      : str|int                         = logmod.WARNING
    format                     : str                             = DEFAULT_FORMAT
    filter                     : list[str]                       = []
    allow                      : list[str]                       = []
    colour                     : bool|str                        = False
    verbosity                  : int                             = 0
    target                     : list[str|pl.Path]               = [] # stdout | stderr | file
    filename_fmt               : str                             = DEFAULT_FILE_FORMAT
    propagate                  : bool                            = False
    clear_handlers             : bool                            = False
    style                      : str                             = DEFAULT_STYLE
    nested                     : list[LoggerSpec]                = []
    prefix                     : Maybe[str]                      = None
    ##--| internal
    _logger                    : Maybe[API.Logger]               = None
    _applied                   : bool                            = False

    @staticmethod
    def build(data:bool|list|dict, **kwargs:Any) -> LoggerSpec:  # noqa: ANN401, FBT001
        """
          Build a single spec, or multiple logger specs targeting the same logger
        """
        match data:
            case LoggerSpec():
                return data
            case False:
                return LoggerSpec(disabled=True, **kwargs)
            case True:
                return LoggerSpec(**kwargs)
            case list():
                nested = []
                for x in data:
                    nested.append(LoggerSpec.build(x, **kwargs))
                return LoggerSpec(nested=nested, **kwargs)
            case ChainGuard():
                as_dict = dict(data)
                as_dict.update(kwargs)
                return LoggerSpec.model_validate(as_dict)
            case dict():
                as_dict = data.copy()
                as_dict.update(kwargs)
                return LoggerSpec.model_validate(as_dict)
            case _:
                msg = "Unknown data for logger spec"
                raise TypeError(msg, data)

    ##--| Validators

    @field_validator("level")
    def _validate_level(cls, val:str|int) -> int:  # noqa: N805
        match val:
            case str() if (lvl:=logmod.getLevelNamesMapping().get(val, None)) is not None:
                return lvl
            case str() if val in LoggerSpec.levels.__members__:
                return LoggerSpec.levels[val]
            case int():
                return val
            case _:
                raise ValueError(val)

    @field_validator("format")
    def _validate_format(cls, val:str) -> str:  # noqa: N805
        return val

    @field_validator("target", mode="before")
    def _validate_target(cls, val:list|str|pl.Path) -> list[str|pl.Path]:  # noqa: N805
        match val:
            case [*xs] if all(x in API.TARGETS for x in xs):
                return val
            case str() if val in API.TARGETS:
                return [val]
            case pl.Path():
                return [val]
            case None:
                return ["stdout"]
            case _:
                msg = "Unknown target value for LoggerSpec"
                raise ValueError(msg, val)

    @field_validator("style")
    def _validate_style(cls, val:str) -> str:  # noqa: N805
        match val:
            case "%" | "{" | "$":
                return val
            case _:
                msg = "API.Logger Style Needs to be in [{,%,$]"
                raise ValueError(msg, val)

    ##--| methods

    @ftz.cached_property
    def fullname(self) -> str:
        if self.base is None:
            return self.name
        return f"{self.base}.{self.name}"

    def apply(self, *, onto:Maybe[API.Logger]=None) -> API.Logger:  # noqa: PLR0912, PLR0915
        """ Apply this spec (and nested specs) to the relevant logger """
        logger : logmod.Logger
        match onto:
            case logmod.Logger() if self._applied:
                msg = "Tried to apply logger when spec already has a logger"
                raise ValueError(msg, self.fullname)
            case logmod.Logger():
                logger = onto
            case None if self._applied:
                # already set up, just return it
                return self.get()
            case None:
                # not set up, get it and set it
                logger = self.get()

        handler_pairs : list[tuple[Maybe[Handler], Maybe[Formatter]]] = []
        logger.propagate = self.propagate
        logger.setLevel(logmod._nameToLevel.get("NOTSET", 0))
        if self.disabled:
            logger.disabled = True
            return logger

        match self.prefix:
            case str() if hasattr(logger, "set_prefixes"):
                logger.set_prefixes(self.prefix)
            case _:
                pass

        match self.colour:
            case str():
                logger.set_colour(self.colour)
            case _:
                pass

        match self.target:
            case _ if bool(self.nested):
                for subspec in self.nested:
                    subspec.apply(onto=logger)
                else:
                    return logger
            case []:
                handler_pairs.append(self._discriminate_handler(None))
            case [*xs]:
                handler_pairs += [self._discriminate_handler(x) for x in xs]
            case _:
                msg = "Unknown target value for LoggerSpec"
                raise ValueError(msg, self.target)

        log_filters = self._build_filters()
        for pair in handler_pairs:
            match pair:
                case None, _:
                    pass
                case hand, None:
                    hand.setLevel(self.level)
                    for fltr in log_filters:
                        hand.addFilter(fltr)
                    else:
                        logger.addHandler(hand)
                case hand, fmt:
                    hand.setLevel(self.level)
                    hand.setFormatter(fmt)
                    for fltr in log_filters:
                        hand.addFilter(fltr)
                    else:
                        logger.addHandler(hand)
                case _:
                    pass
        else:
            if not bool(logger.handlers):
                logger.setLevel(self.level)
                logger.propagate = True

            self._applied = True
            self._logger  = logger
            return logger

    def get(self) -> API.Logger:
        """ Get the logger  this spec controls """
        if self._logger is None:
            self._logger = logmod.getLogger(self.fullname)

        return self._logger

    def clear(self) -> None:
        """ Clear the handlers for the logger referenced """
        logger = self.get()
        handlers = logger.handlers[:]
        for h in handlers:
            logger.removeHandler(h)

        self._logger = None

    def logfile(self) -> pl.Path:
        log_dir  = pl.Path(".temp/logs")
        if not log_dir.exists():
            log_dir = pl.Path()

        filename = datetime.datetime.now().strftime(self.filename_fmt)  # noqa: DTZ005
        return log_dir / filename

    def set_level(self, level:int|str) -> None:
        match level:
            case str():
                level = logmod._nameToLevel.get(level, 0)
            case int():
                pass
        logger = self.get()
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
