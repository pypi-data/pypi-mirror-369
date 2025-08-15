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

from .core import MetalordCore
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

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class MLSingleton(MetalordCore):
    """
    Metaclass for enforcing singletons

    with force_new=True, dont reuse the singleton
    """
    def __call__(cls, *args:Any, **kwargs:Any):
        match kwargs.pop("force_new", False):
            case True:
                obj = object.__new__(cls)
                obj.__init__(*args, **kwargs)
                return obj
            case _ if not hasattr(cls, "__inst"):
                logging.debug("Creating Singleton %s", cls.__name__)
                obj = object.__new__(cls)
                obj.__init__(**kwargs)
                setattr(cls, "__inst", obj)

        return getattr(cls, "__inst")
