#!/usr/bin/env python3
"""



"""
# Import:
from __future__ import annotations
from typing import Final, Self
from jgdv.debugging import TraceBuilder

##--| Error Messages
ErrorMSg_1 : Final[str] = "Test Message"


##--| Errors
class JGDVError(Exception):
    """ A Base Error Class for JGDV """

    def __getitem__(self, val:None|int|slice) -> Self:
        """ Use jgdv.debugging.TraceBuilder to control the traceback
        of this error

        """
        match val:
            case int() as x:
                return self.with_traceback(TraceBuilder()[slice(x)])
            case slice(start=None) as x:
                adjusted = slice(1, x.stop, x.step)
                return self.with_traceback(TraceBuilder()[adjusted])
            case slice(start=int() as start) as x:
                adjusted = slice(1+start, x.stop, x.step)
                return self.with_traceback(TraceBuilder()[adjusted])
            case _:
                return self.with_traceback(TraceBuilder()[1:])
