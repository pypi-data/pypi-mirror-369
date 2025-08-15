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
import string
import time
import types
import weakref
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 1st party imports
from jgdv.structs.strang import CodeReference

# ##-- end 1st party imports

from .._interface import DKeyMark_e
from .._util._interface import ExpInst_d, InstructionFactory_p
from ..dkey import DKey
from ..keys import MultiDKey, NonDKey, SingleDKey

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, Generic, cast, assert_type, assert_never
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload

if TYPE_CHECKING:
    from jgdv import Maybe, Ident, RxStr, Rx
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

class PathDKey(DKey[list], mark=pl.Path):
    """
    A Simple key that always expands to a path, and is then normalised
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data.convert         = "p"
        self.data.expansion_type  = pl.Path
        self.data.typecheck       = pl.Path

    def exp_coerce_h(self, inst:ExpInst_d, factory:InstructionFactory_p, opts:dict) -> Maybe[ExpInst_d]:
        val = pl.Path(inst.value)
        if 'relative' not in opts:
            val = val.expanduser().resolve()
        return factory.literal_inst(val)

    def exp_final_h(self, inst:ExpInst_d, root:Maybe[ExpInst_d], factory:InstructionFactory_p, opts:dict) -> Maybe[ExpInst_d]:
        return factory.literal_inst(inst.value)
