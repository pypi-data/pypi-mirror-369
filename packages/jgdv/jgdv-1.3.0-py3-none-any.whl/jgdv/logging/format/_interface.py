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
# General
import abc
import collections.abc
import typing
import types
from typing import cast, assert_type, assert_never
from typing import Generic, NewType, Never
from typing import no_type_check, final, override, overload
# Protocols and Interfaces:
from typing import Protocol, runtime_checkable
# isort: on
# ##-- end types

# ##-- type checking
# isort: off
if typing.TYPE_CHECKING:
    from typing import Final, ClassVar, Any, Self
    from typing import Literal, LiteralString
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from jgdv import Maybe
## isort: on
# ##-- end type checking

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
default_log_colours : Final[dict[int, tuple[str, str]]] = {
    logmod.DEBUG    : ("fg", "grey"),
    logmod.INFO     : ("fg", "blue"),
    logmod.WARNING  : ("fg", "yellow"),
    logmod.ERROR    : ("fg", "red"),
    logmod.CRITICAL : ("fg", "red"),
}

default_colour_mapping : Final[dict[str, tuple[str,str]]] = {
    "blue"           : ("fg", "blue"),
    "cyan"           : ("fg", "cyan"),
    "green"          : ("fg", "green"),
    "magenta"        : ("fg", "magenta"),
    "red"            : ("fg", "red"),
    "yellow"         : ("fg", "yellow"),
    "bg_blue"        : ("bg", "blue"),
    "bg_cyan"        : ("bg", "cyan"),
    "bg_green"       : ("bg", "green"),
    "bg_magenta"     : ("bg", "magenta"),
    "bg_red"         : ("bg", "red"),
    "bg_yellow"      : ("bg", "yellow"),
    "bold"           : ("ef", "bold"),
    "underline"      : ("ef", "u"),
    "italic"         : ("ef", "italic"),
    "RESET"          : ("rs", "all"),
}
# Body:
