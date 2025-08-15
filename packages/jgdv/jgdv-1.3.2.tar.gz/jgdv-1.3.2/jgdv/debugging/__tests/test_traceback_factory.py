#!/usr/bin/env python3
"""
TEST File updated

"""
# ruff: noqa: ANN202, B011

# Imports
from __future__ import annotations

# ##-- stdlib imports
import logging as logmod
import pathlib as pl
import warnings
# ##-- end stdlib imports

# ##-- 3rd party imports
import pytest
# ##-- end 3rd party imports


##--|
from ..traceback_factory import TracebackFactory
##--|

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

# Body:
class TestTracebackFactory:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match TracebackFactory():
            case TracebackFactory():
                assert(True)
            case x:
                assert(False), x

    def test_basic(self):
        obj = TracebackFactory()
        match obj.to_tb():
            case types.TracebackType():
                assert(True)
            case x:
                assert(False), x


    def test_getitem(self):
        obj = TracebackFactory()
        match obj[:1]:
            case types.TracebackType():
                assert(True)
            case x:
                assert(False), x

    def test_classitem(self):
        match TracebackFactory[:1]:
            case types.TracebackType():
                assert(True)
            case x:
                assert(False), x
