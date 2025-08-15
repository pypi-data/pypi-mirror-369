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
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

from jgdv._abstract.protocols.pre_processable import PreProcessor_p
from jgdv.structs.strang import _interface as StrangAPI  # noqa: N812
from jgdv.structs.strang.processor import StrangBasicProcessor
from . import _interface as API # noqa: N812

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
if typing.TYPE_CHECKING:
    from jgdv._abstract.protocols.pre_processable import InstanceData, PostInstanceData
    from typing import Final, ClassVar, Any, Self
    from typing import Literal, LiteralString
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from jgdv._abstract.protocols.pre_processable import PreProcessResult
    from jgdv import Maybe, Ctor

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class LocationProcessor[T:API.Location_p](StrangBasicProcessor):

    @override
    def pre_process(self, cls:type[T], input:Any, *args:Any, strict:bool=False, **kwargs:Any) -> PreProcessResult[T]: # type: ignore[override]  # noqa: PLR0912, PLR0915
        assert(cls.section(0).case is not None)
        assert(cls.section(1).case is not None)
        x             : Any
        y             : Any
        default_mark  : Maybe[StrangAPI.StrangMarkAbstract_e]
        head_end      : str
        text          : str
        head_case     : str                             = cast("str", cls.section(0).case)
        body_case     : str                             = cast("str", cls.section(1).case)
        head_text     : set[str]                        = set()
        body_text     : list[str]                       = []
        inst_data     : InstanceData                    = {}
        post_data     : PostInstanceData                = {}
        marks         : StrangAPI.StrangMarkAbstract_e  = cls.Marks
        ctor          : Ctor[T]                         = cls
        match cls.section(0).end:
            case None:
                raise ValueError()
            case str() as x:
                head_end                                = x

        match marks.default():
            case None:
                raise ValueError()
            case x:
                default_mark  = marks.default()
        ##--| clean the input
        match input:
            case StrangAPI.Strang_p() as val:
                x, m, y = val[:,:].partition(head_end)
                if bool(m):
                    head_text.update(x.split(head_case))
                    body_text.append(y)
                else:
                    body_text.append(x)
            case pl.Path() as val if bool(val.suffix):
                head_text.add(marks.file) # type: ignore[attr-defined]
                body_text.append(str(val))
            case str() as val:
                x, m, y = val.partition(head_end)
                if bool(m):
                    head_text.update(x.split(head_case))
                    body_text.append(y)
                else:
                    body_text.append(x)
            case val:
                x, m, y = str(val).partition(head_end)
                if bool(m):
                    head_text.update(x.split(head_case))
                    body_text.append(y)
                else:
                    body_text.append(x)


        body : str = body_case.join(body_text)
        s1_marks = cls.section(1).marks
        assert(s1_marks is not None)
        if any(x.value in body for x in s1_marks):
            head_text.add(marks.abstract.value) # type: ignore[attr-defined]
        if "." in body:
            head_text.add(marks.file.value) # type: ignore[attr-defined]

        if not bool(head_text) and default_mark is not None:
            head_text.add(default_mark)
        assert(bool(body_text))
        text = head_end.join([head_case.join(head_text), body])
        return text, inst_data, post_data, ctor

