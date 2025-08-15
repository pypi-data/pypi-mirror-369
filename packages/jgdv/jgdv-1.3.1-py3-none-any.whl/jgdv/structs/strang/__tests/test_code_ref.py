#!/usr/bin/env python3
"""

"""
# ruff: noqa: ANN202, B011
from __future__ import annotations

import logging as logmod
import pathlib as pl
from typing import (Any, ClassVar, Generic, TypeAlias, TypeVar, cast, Final)
import warnings

import pytest
logging = logmod.root

from jgdv import identity_fn
from jgdv.structs.strang import Strang
from jgdv.structs.strang import _interface as API  # noqa: N812
from jgdv.structs.strang.code_ref import CodeReference

EX_STR     : Final[str]  = "fn::jgdv:identity_fn"
NO_PREFIX  : Final[str]  = "jgdv:identity_fn"

class TestCodeReference:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_basic(self):
        ref = CodeReference(EX_STR)
        assert(isinstance(ref, CodeReference))
        assert(ref == EX_STR)

    def test_annotated(self):
        ref = CodeReference[bool]
        assert(issubclass(ref, CodeReference))
        assert(ref.cls_annotation() == (bool,))
        inst = ref(EX_STR)
        assert(isinstance(inst, CodeReference))

    def test_with_no_prefix(self):
        ref = CodeReference(NO_PREFIX)
        assert(isinstance(ref, CodeReference))

    def test_instance(self):
        ref = CodeReference(EX_STR)
        assert(isinstance(ref, CodeReference))

    def test_with_value(self):
        ref = CodeReference(EX_STR, value=int)
        assert(isinstance(ref, CodeReference))

    def test_str(self):
        ref = CodeReference(EX_STR)
        assert(str(ref) == EX_STR)

    def test_repr(self):
        ref = CodeReference(EX_STR)
        assert(repr(ref) == f"<CodeReference: {EX_STR}>")

    def test_module(self):
        ref = CodeReference(EX_STR)
        assert(ref[1,0] == "jgdv")
        assert(ref.module == "jgdv")

    def test_value(self):
        ref = CodeReference(EX_STR)
        assert(ref[2,0] == "identity_fn")
        assert(ref.value == "identity_fn")

    @pytest.mark.xfail
    def test_from_fn(self):

        def simple_fn():
            return "blah"

        ref = CodeReference(simple_fn)
        assert(ref() is simple_fn)

class TestCodeReference_Importing:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_import(self):
        ref      = CodeReference(EX_STR)
        match ref(check=False):
            case Exception() as x:
                assert(False), x
            case x:
                assert(callable(x))
                assert(x == identity_fn)

    def test_import_module_fail(self):
        ref = CodeReference("cls::jgdv.taskSSSSS.base_task:DootTask")
        match ref():
            case ImportError():
                assert(True)
            case x:
                assert(False), x

    def test_import_non_existent_class_fail(self):
        ref = CodeReference("cls::jgdv.structs.strang:DootTaskSSSSSS")
        match ref():
            case ImportError():
                assert(True)
            case _:
                assert(False)

    def test_import_non_class_fail(self):
        ref = CodeReference("cls::jgdv.structs.strang.strang:GEN_K")
        match ref():
            case ImportError():
                assert(True)
            case _:
                assert(False)

    def test_import_non_callable(self):
        ref = CodeReference("fn::jgdv.structs.strang.strang:GEN_K")
        match ref():
            case ImportError():
                assert(True)
            case _:
                assert(False)

    def test_import_value(self):
        ref = CodeReference("val::jgdv.structs.strang._interface:GEN_K")
        assert(ref[0,:] == "val")
        assert(ref[1,:] == "jgdv.structs.strang._interface")
        assert(ref[2,:] == "GEN_K")
        match ref(check=False):
            case str() as x:
                assert(x == API.GEN_K)
            case ImportError():
                assert(False)
            case _:
                assert(True)

class TestCodeReference_TypeCheck:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_basic_typecheck(self):
        ref = CodeReference[Strang]("cls::jgdv.structs.strang:Strang")
        match ref():
            case type() as x if x == Strang:
                assert(True)
            case x:
                assert(False), x

    def test_union_typecheck(self):
        ref = CodeReference[int|Strang]("cls::jgdv.structs.strang:Strang")
        assert(ref.expects_type() == int|Strang)
        match ref():
            case type() as x if x == Strang:
                assert(True)
            case x:
                assert(False), x

    def test_typecheck_fail(self):
        ref = CodeReference[bool]("cls::jgdv.structs.strang:Strang")
        assert(ref.expects_type() is bool)
        match ref():
            case ImportError():
                assert(True)
            case x:
                assert(False), x

    def test_union_typecheck_fail(self):
        ref = CodeReference[bool|int]("cls::jgdv.structs.strang:Strang")
        assert(ref.expects_type() == bool|int)
        match ref():
            case ImportError():
                assert(True)
            case x:
                assert(False), x

    def test_explicit_typecheck(self):
        ref = CodeReference("cls::jgdv.structs.strang:Strang")
        assert(ref.expects_type() is None)
        match ref(check=Strang):
            case type():
                assert(True)
            case x:
                assert(False), x

    def test_explicit_union_typecheck(self):
        ref = CodeReference("cls::jgdv.structs.strang:Strang")
        assert(ref.expects_type() is None)
        match ref(check=int|Strang):
            case type():
                assert(True)
            case x:
                assert(False), x

class TestCodeReference_Annotate:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_no_annotation(self):
        basic = CodeReference(EX_STR)
        assert(basic._check is None)
        assert(basic.expects_type() is None)


    def test_annotation_doesnt_override_super(self):
        basic = CodeReference(EX_STR)
        assert(basic._check is None)
        assert(basic.expects_type() is None)
        other = CodeReference[int](EX_STR)
        assert(basic.expects_type() != other.expects_type())


    def test_annotation_doesnt_register(self):
        basic = CodeReference
        anno1 = CodeReference[int]
        anno2 = CodeReference[int|str]
        anno3 = CodeReference[str|Strang|float]

        for x in [basic, anno1, anno2, anno3]:
            assert(x not in CodeReference._registry)

    def test_simple(self):
        basic = CodeReference[int](EX_STR)
        assert(basic._check is int)
        assert(basic.expects_type() is int)

    def test_union(self):
        basic = CodeReference[int|str](EX_STR)
        assert(basic._check == int|str)
        assert(basic.expects_type() == int|str)
