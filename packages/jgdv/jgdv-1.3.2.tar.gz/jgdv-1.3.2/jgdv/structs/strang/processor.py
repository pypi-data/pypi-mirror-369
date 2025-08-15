#!/usr/bin/env python3
"""

"""
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
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
# ##-- end stdlib imports

from collections import defaultdict
from jgdv import Proto, Mixin
from jgdv._abstract.protocols.pre_processable import PreProcessor_p
from . import errors
from . import _interface as API  # noqa: N812

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType, Never
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload
from collections.abc import Callable

if TYPE_CHECKING:
    import enum
    from jgdv import Maybe, MaybeT
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from ._interface import Strang_p
    from jgdv._abstract.protocols.pre_processable import PreProcessResult, InstanceData, PostInstanceData
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--| Vars
HEAD_IDXS : Final[int] = 1
##--| funcs

def name_to_hook(val:str) -> str:
    return f"_{val}_h"

##--| Body

class StrangBasicProcessor[T:Strang_p](PreProcessor_p):
    """ A processor for basic strangs,
    the instance is assigned into Strang._processor

    If the strang type implements _{call}_h,
    the processor uses that for a stage instead
    """

    def use_hook(self, cls:type[T]|T, stage:str, *args:Any, **kwargs:Any) -> MaybeT[bool, Any]:  # noqa: ANN401
        result : MaybeT[bool, Any]
        match cls, getattr(cls, name_to_hook(stage), None):
            case _, None:
                return None
            case _, x if not callable(x):
                return None
            case type(), x:
                assert(callable(x))
                result = x(*args, **kwargs)
            case _, x:
                assert(callable(x))
                result = x(*args, **kwargs)

        match result:
            case None:
                return None
            case bool() as prefer, *rest:
                return (prefer, *rest)
            case x:
                        raise TypeError(type(x))

    @override
    def pre_process(self, cls:type[T], input:Any, *args:Any, strict:bool=False, **kwargs:Any) -> PreProcessResult[T]:
        """ run before str.__new__ is called,
        to do early modification of the string
        Filters out extraneous duplicated separators
        """
        base_text   : str
        final_text  : str
        extracted   : dict
        inst_data   : InstanceData      = {}
        post_data   : PostInstanceData  = {}
        ctor        : Maybe[type[T]]    = None
        skip_mark   : str               = cls.section(-1).case or ""

        match args:
            case []:
                base_text = str(input)
            case [*xs, x] if "[" in x and "]" in x:
                base_body =  skip_mark.join(str(x) for x in [input, *xs])
                base_text = f"{base_body}{x}"
            case [*xs]:
                base_text  = skip_mark.join(str(x) for x in [input, *xs])

        match self.use_hook(cls, "pre_process", input, *args, strict=strict, **kwargs):
            case None:
                pass
            case False, *rest:
                base_text , inst_data, post_data, ctor = rest  # type: ignore[assignment]
                return base_text, inst_data, post_data, ctor
            case True, *rest:
                base_text, inst_data, post_data, ctor = rest  # type: ignore[assignment]

        if not self._verify_structure(cls, base_text):
            raise ValueError(errors.MalformedData, base_text)

        clean                  = self._clean_separators(cls, base_text).strip()
        final_text, extracted  = self._compress_types(cls, clean)
        assert(not ('types' in extracted and 'types' in post_data))
        post_data.update(extracted)
        match self._get_args(final_text):
            case int() as args_start:
                post_data['args_start']  = args_start
            case _:
                pass

        return final_text, inst_data, post_data, None

    def _verify_structure(self, cls:type[T], val:str) -> bool:
        """ Verify basic strang structure.

        ie: all necessary sections are, provisionally, there.
        """
        seps = [x.end for x in cls._sections.order if x.end is not None and x.required]
        return all(x in val for x in seps)

    def _clean_separators(self, cls:type[T], val:str) -> str:
        """ Clean even repetitions of the separator down to single uses

        eg: for sep='.',
        a..b::c....d -> a.b::c.d
        but:
        a.b::c...d -> a.b::c..d
        """
        # TODO join the seps
        seps = [x.case for x in cls._sections.order]
        sep = seps[0] or ""
        sep_double = re.escape(sep * 2)
        clean_re   = re.compile(f"{sep_double}+")
        # Don't reuse sep_double, as thats been escaped
        cleaned    = clean_re.sub(sep * 2, val)
        trimmed    = cleaned.removesuffix(sep).removesuffix(sep)
        return trimmed

    def _compress_types(self, cls:type[T], val:str) -> tuple[str, dict]:  # noqa: ARG002
        """ Extract values of explicitly typed words.

        allows the base str of the Strang to be readable,
        and for post-process to insert types as necessary

        eg: a.b.c::d.e.<uuid:....> -> (a.b.c::d.e.<uuid>, {uuids:[UUIDstr]}

        """
        curr       : re.Match
        text       : list                          = []
        extracted  : list[tuple[str, Maybe[str]]]  = []
        idx        : int                           = 0
        for curr in API.TYPE_ITER_RE.finditer(val):
            match curr.groups():
                case ["<", str() as key, str() as oval, ">"]:
                    extracted.append((key, oval))
                    _,start         = curr.span(2)
                    rest,end        = curr.span(4)
                    text.append(val[idx:start])
                    text.append(val[rest:end])
                    idx = end
                case ["<", str() as key, None, ">"]:
                    extracted.append((key, None))
        else:
            text.append(val[idx:])
            return "".join(text), {'types': extracted}

    def _get_args(self, val:str) -> Maybe[int]:
        try:
            idx : int = val.rindex(API.ARGS_CHARS[0])
            assert(val[-1] == API.ARGS_CHARS[-1])
            assert(API.ARGS_RE.match(val[idx:]))
        except ValueError:
            return None
        else:
            return idx

    ##--|

    @override
    def process(self, obj:T, *, data:PostInstanceData) -> Maybe[T]:
        """ slice the sections of the strang

        populates obj.data:
        - slices
        - flat
        - bounds
        """
        pos_offset    : int
        word_indices  : list[tuple[int, ...]]
        sec_slices    : list[slice]
        flat_slices   : list[slice]
        match self.use_hook(obj, "process", data=data):
            case None:
                pass
            case True, x:
                assert(isinstance(x, type(obj)|None))
                return x
            case False, None:
                pass
            case False, x:
                assert(isinstance(x, type(obj)))
                obj = x

        logging.debug("Processing Strang: %s", str.__str__(obj))
        match data:
            case {"args_start": int() as arg_s}:
                obj.data.args_start = arg_s
            case _:
                pass

        pos_offset, index_offset = 0, 0
        sec_slices, flat_slices, word_indices = [], [], []
        for section in obj.sections():
            sec, words, extend = self._process_section(obj, section, start=pos_offset)
            sec_slices.append(sec)
            word_indices.append(tuple(range(index_offset, index_offset+len(words))))
            index_offset += len(words)
            flat_slices  += words
            pos_offset    = sec.stop + extend
        else:
            obj.data.sec_words  = tuple(word_indices)
            obj.data.flat_idx   = tuple((i,j) for i,x in enumerate(obj.data.sec_words) for j in range(len(x)))
            obj.data.sections   = tuple(sec_slices)
            obj.data.words      = tuple(flat_slices)
            self._process_args(obj, data=data)
            return None

    def _process_section(self, obj:T, section:API.Sec_d, *, start:int=-1) -> tuple[slice, tuple[slice, ...], int]:
        """ Set the slices of a section, return the index where the section ends """
        word_slices   : tuple[slice]
        search_end    : int  = obj.data.args_start or len(obj)
        bound_extend  : int  = 0
        match section.end:
            case str() as x:
                try:
                    bound_extend = len(x)
                    search_end   = obj.index(x, start=start)
                except (ValueError, TypeError):
                    return slice(start, start), (), 0
            case None:
                pass
        ##--|

        word_slices = self._slice_section(obj,
                                          case=[section.case, section.end],
                                          start=start,
                                          max=search_end)
        assert(all((start <= x.start <= x.stop <= search_end) for x in word_slices))
        match word_slices:
            case []:
                return slice(start, search_end), (), 0
            case _:
                return slice(start, search_end), word_slices, bound_extend

    def _slice_section(self, obj:T, *, case:list[Maybe[str]], start:int=0, max:int=-1) -> tuple[slice]:  # noqa: A002
        """ Get a list of word slices of a section, with an offset. """
        curr    : re.Match
        slices  : list[slice]  = []
        end                    = max or len(obj)
        escaped                = "|".join(re.escape(x) for x in case if x is not None)
        reg                    = re.compile(f"(.*?)({escaped}|$)")
        words                  = []
        for curr in reg.finditer(cast("str", obj), start, end):
            span = curr.span(1)
            if span[0] == end:
                continue
            slices.append(slice(*span))
            words.append(obj[span[0]:span[1]])
        else:
            return cast("tuple[slice]", tuple(slices))

    def _process_args(self, obj:T, *, data:dict) -> None:
        """ Extract args and set values as necessary """
        if not (arg_s:=obj.data.args_start):
            return

        selection = sorted([x.strip() for x in API.STRGET(obj, slice(arg_s+1, -1)).split(API.ARGS_CHARS[1])])
        if len(selection) != len(set(selection)):
            raise ValueError(selection)

        obj.data.args = tuple(selection)
        if API.UUID_WORD in selection and obj.data.uuid is None:
            assert('types' in data), data
            match data['types'].pop():
                case "uuid", str() as uid_val:
                    obj.data.uuid = UUID(uid_val)
                case "uuid", None:
                    obj.data.uuid = uuid1()
                case _:
                    pass

    ##--|

    @override
    def post_process(self, obj:T, data:PostInstanceData) -> Maybe[T]:
        """ With the strang cleaned and slices, build meta data for words

        takes the data extracted during pre-processing.

        """
        metas  : list  = []
        if 'types' in data:
            data['types'].reverse()

        match self.use_hook(obj, "post_process", data=data):
            case None:
                pass
            case True, x:
                assert(isinstance(x, type(obj)|None))
                return x
            case False, None:
                pass
            case False, x:
                assert(isinstance(x, type(obj)))
                obj = x

        logging.debug("Post-processing Strang: %s", str.__str__(obj))
        for i in range(len(obj.sections())):
            metas += self._post_process_section(obj, i, data)
        else:
            obj.data.meta = tuple(metas)  # type: ignore[assignment]
            self._validate_marks(obj)
            self._calc_obj_meta(obj)
            return None

    def _post_process_section(self, obj:T, idx:int, data:dict) -> list:
        type MetaTypes              = Maybe[UUID|API.StrangMarkAbstract_e|int]
        elem     : str
        section  : API.Sec_d        = obj.section(idx)
        count    : int              = len(obj.data.sec_words[idx])
        meta     : list[MetaTypes]  = [None for x in range(count)]
        ##--|
        for i, word_idx in enumerate(obj.data.sec_words[idx]):
            elem                    = obj[obj.data.words[word_idx]]
            assert(isinstance(elem, str))
            # Discriminate the str
            match elem:
                case x if (mark_elem:=self._implicit_mark(x, sec=section, data=data, index=i, maxcount=count)) is not None:
                    logging.debug("(%s) Found Named Marker: %s", i, mark_elem)
                    meta[i] = mark_elem
                case x if (type_mark:=self._make_type(x, sec=section, data=data, obj=obj)) is not None:
                    meta[i] = type_mark
                case x if (mark_elem:=self._build_mark(x, sec=section, data=data)) is not None:
                    logging.debug("(%s) Found Named Marker: %s", i, mark_elem)
                    meta[i] = mark_elem
                case _: # nothing special
                    pass
        else:
            return meta

    def _validate_marks(self, obj:T) -> None:
        """ Check marks make sense.
        eg: +|_ are only at obj[1:0]

        """
        pass

    def _calc_obj_meta(self, obj:T) -> None:
        """ Set object level meta dict

        ie: mark the obj as an instance
        """
        pass

    ##--| utils

    def _make_type(self, val:str, *, sec:API.Sec_d, data:dict, obj:T) -> Maybe[Any]:  # noqa: ARG002
        """ Handle <type> words, which may have had data extracted during pre-processing.

        """
        key      : str
        typeval  : Maybe[str]
        result   : Maybe  = None
        if not (word:=API.TYPE_RE.match(val)):
            return None

        match data.get('types', [None]).pop():
            case None: # No types data remains
                raise ValueError()
            case str() as key, typeval:
                pass

        match word.groups()[0], typeval:
            case x, _ if x != key: # Mismatch between types
                raise ValueError(x, key)
            case "uuid", None:
                result = uuid1()
            case "uuid", str() as spec:
                result = UUID(spec)
            case "int", str() as spec:
                result = int(spec)
            case [x, _]:
                raise ValueError()

        ##--|
        return result

    def _build_mark(self, val:str, *, sec:API.Sec_d, data:dict) -> Maybe[API.StrangMarkAbstract_e]:  # noqa: ARG002
        """ converts applicable words to mark enum values
        Matches using strang._interface.MARK_RE

        """
        match sec.marks:
            case None:
                return None
            case x:
                marks = x
        match API.MARK_RE.match(val):
            case re.Match() as matched if (key:=matched[1]) is not None:
                if key.lower() in marks:
                    return marks(key)
                return None
            case _:
                return None

    def _implicit_mark(self, val:str, *, sec:API.Sec_d, data:dict, index:int, maxcount:int) -> Maybe[API.StrangMarkAbstract_e]:  # noqa: ARG002
        """ Builds certain implicit marks,
        but only for the first and last words of a section

        # TODO handle combined marks like val::+_.blah

        """
        x : Any
        first_or_last = index in {0, maxcount-1}
        match sec.marks:
            case None:
                return None
            case x:
                marks = x
        match marks.skip():
            case None:
                pass
            case x if val == x:
                return cast("API.StrangMarkAbstract_e", x)

        if not (first_or_last and val in marks):
            return None
        return marks(val)

    def prep_word(self, val:API.PushVal, *, fallback:str|API.StrangMarkAbstract_e="") -> str:
        result : str
        match val:
            case API.StrangMarkAbstract_e() as x if x in type(x).idempotent():
                result =  x.value
            case str() as x:
                result =  x
            case UUID() as x:
                result =  f"<uuid:{x}>"
            case None:
                result =  fallback
            case x:
                result =  str(x)

        return result
