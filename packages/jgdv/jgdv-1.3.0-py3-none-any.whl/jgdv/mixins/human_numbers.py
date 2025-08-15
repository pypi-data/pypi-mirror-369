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
import tracemalloc
import types
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref

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
from typing import no_type_check, final, override, overload

if TYPE_CHECKING:
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from jgdv import DateTime, Seconds
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

class HumanNumbers_m:
    """
    Simple Mixin for human related functions
    """

    @staticmethod
    def humanize(val:int|float, *, force_sign:bool=True) -> str:
        """ Format {val} in a human readable way as a size.
        Uses tracemalloc._format_size.
        Depending on size, will use on of the units:
        B, KiB, MiB, GiB, TiB.
        """
        return tracemalloc._format_size(val, force_sign) # type:ignore[attr-defined]


    @staticmethod
    def round_time(dt:DateTime=None, *,  round:Seconds=60) -> DateTime:
        """Round a datetime object to any time lapse in seconds
        dt : datetime.datetime object, default now.
        round : Closest number of seconds to round to, default 1 minute.
        Author: Thierry Husson 2012 - Use it as you want but don't blame me.
        from: https://stackoverflow.com/questions/3463930
        """
        dt       = dt or datetime.datetime.now()
        seconds  = (dt.replace(tzinfo=None) - dt.min).seconds
        rounding = (seconds+round/2) // round * round
        return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)
