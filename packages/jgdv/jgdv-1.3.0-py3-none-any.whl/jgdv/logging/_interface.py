#!/usr/bin/env python3
"""

"""
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final

if TYPE_CHECKING:
    from jgdv import Maybe
    from jgdv.structs.chainguard import ChainGuard
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Types
type Logger      = logmod.Logger
type Formatter   = logmod.Formatter
type Handler     = logmod.Handler
type LoggerSpec  = Any

# Vars:
LOGDEC_PRE      : Final[str]       = "__logcall__"
PRINTER_NAME    : Final[str]       = "_printer_"
MAX_FILES       : Final[int]       = 5
TARGETS         : Final[list[str]] = [
    "file", "stdout", "stderr", "rotate", "pass",
]

default_stdout  : Final[dict]      = {
    "name"           : logmod.root.name,
    "level"          : "user",
    "target"         : ["stdout"],
    "format"         : "{levelname}  : INIT : {message}",
    "style"          : "{",
    }
default_printer : Final[dict]      = {
    "name"           : PRINTER_NAME,
    "level"          : "user",
    "target"         : ["stdout"],
    "format"         : "{name}({levelname}) : {message}",
    "style"          : "{",
    "propagate"      : False,
    }
default_print_file : Final[str]    = "print.log"

alt_log_colours : Final[dict[int, tuple[str, str]]] = {
    logmod.DEBUG    : ("fg", "grey"),
    logmod.INFO     : ("fg", "green"),
    logmod.WARNING  : ("fg", "blue"),
    logmod.ERROR    : ("fg", "red"),
    logmod.CRITICAL : ("fg", "red"),
}

# Body:

class LogLevel_e(enum.IntEnum):
    """ My Preferred Loglevel names """
    error     = logmod.ERROR   # Total Failures
    user      = logmod.WARNING # User Notification
    trace     = logmod.INFO    # Program Landmarks
    detail    = logmod.DEBUG   # Exact values
    bootstrap = logmod.NOTSET  # Startup before configuration
##--|

class LogConfig_p(Protocol):
    """ The interface of how logging is configured. """

    def setup(self, config:dict|ChainGuard) -> None: ...

    def set_level(self, level:int|str) -> None: ...

    def subprinter(self, *names:str) -> Logger: ...

    def activate_spec(self, spec:LoggerSpec, *, override:bool=False) -> None: ...

    def report(self) -> None: ...

    def reset(self) -> None: ...
