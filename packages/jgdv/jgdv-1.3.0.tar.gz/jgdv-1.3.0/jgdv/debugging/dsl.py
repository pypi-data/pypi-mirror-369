#/usr/bin/env python3
"""

"""
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import logging as logmod
from copy import deepcopy
from re import Pattern
from uuid import UUID, uuid1
from weakref import ref

# ##-- end stdlib imports

# ##-- 3rd party imports
import pyparsing as pp
import pyparsing.core as ppc

# ##-- end 3rd party imports

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

MARK                      = ">!<"
MATCHING                  = "Matching" + (" " * 17)
MATCHED                   = "Matched"  + ("-" * 14)
FAILED                    = "Failed"   + ("_" * 11)

try_format   : Final[str] = "{3[0]:>10}{3[1]:3}{3[2]:<10} {0} <{1}> at {2}:  "
match_format : Final[str] = "{4[0]:>10}{4[1]:3}{4[2]:<10}\t {0} <{1}> ({2}) {3}"
fail_format  : Final[str] = "{5[0]:>10}{5[1]:3}{5[2]:<10}\t\t {0} <{1}>: {2} found '{3}' at {4}"

class PyParsingDebuggerControl:

    @staticmethod
    def debug_pyparsing(*flags, all_warnings=False) -> None:
        """ Set pyparsing to debug
        Only applies for parsers created *after* this,
        so has to be set at boot time.
        """
        # pylint: disable=protected-access
        if flags is None:
            flags = [pp.Diagnostics.enable_debug_on_named_expressions]
        if not debug_pyparsing_active_p():
            logging.info("Enabling Debug on %s Parsers", "Named")
            pp.__diag__.enable_debug_on_named_expressions = True
            if bool(flags):
                for flag in flags:
                    pp.enable_diag(flag)

            if all_warnings:
                pp.enable_all_warnings()
            ppc._default_success_debug_action                 = debug_match_action
            ppc._default_start_debug_action                   = debug_try_action
            ppc._default_exception_debug_action               = debug_fail_action
        else:
            logging.warning("PyParsing Debug is already active")

    @staticmethod
    def dfs_activate(*parsers, remove=False):
        """ DFS on a parser, adding debug funcs to named sub parsers """
        # pylint: disable=protected-access
        queue = list(parsers)
        found = set()
        while bool(queue):
            current = queue.pop(0)
            if current is None or id(current) in found:
                continue

            found.add(id(current))

            if bool(current.name) and current.name != current._defaultName and not remove:
                current.set_debug_actions(debug_try_action,
                                        debug_match_action,
                                        debug_fail_action)
            elif remove:
                current.set_debug_actions(None, None, None)

            if hasattr(current, 'expr'):
                queue.append(current.expr)
            elif hasattr(current, 'exprs'):
                queue += current.exprs

    @static
    def debug_active_p() -> bool:
        return pp.__diag__.enable_debug_on_named_expressions

def debug_try_action(instring, loc, expr, *args):
    """
    Log Entry into parsers
    """
    # pylint: disable=unused-argument, consider-using-f-string
    context = _calc_mark_string(instring, loc)
    logging.warning(try_format.format(MATCHING, expr.name, loc, context))

def debug_match_action(instring, startloc, endloc, expr, toks, *args):
    """
    Log Parser Success
    """
    # pylint: disable=unused-argument, consider-using-f-string
    context = _calc_mark_string(instring, endloc)
    logging.warning(match_format.format(MATCHED, expr.name, str(toks), endloc, context))

def debug_fail_action(instring, loc, expr, exc, *args):
    """
    Log Parser failure
    """
    # pylint: disable=unused-argument, consider-using-f-string
    if isinstance(exc, pp.ParseBaseException):
        found_str = exc.pstr[exc.loc:exc.loc + 1].replace(r'\\', '\\').replace("\n", "\\n")
        mark_str  = _calc_mark_string(instring, exc.loc)
        msg       = exc.msg
        loc       = exc.loc
    else:
        found_str = "AssertionError"
        mark_str  = ("", "", "")
        msg       = ""
        loc       = ""

    logging.error(fail_format.format(FAILED, expr.name, msg, found_str, loc, mark_str))

## util

def _calc_mark_string(instring, loc, buffer=10):
    str_len  = len(instring)
    pre_str  = instring[max(0, loc-buffer):max(0, loc)]
    post_str = instring[max(0, loc):min(str_len, loc+buffer)]
    return pre_str.replace("\n", "\\n"), MARK, post_str.replace("\n", "\\n")

# except pp.ParseException as err:
#     import traceback
#     traceback.print_tb(err.__traceback__)
#     logging.warning(f"Parse Failure: {err.markInputline()}")
