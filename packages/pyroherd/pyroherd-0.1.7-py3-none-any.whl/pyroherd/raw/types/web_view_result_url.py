#  <<<<<<< HEAD
#  =======
#  <<<<<<< HEAD
#  >>>>>>> c723d0e (update)
#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present OnTheHerd <https://github.com/OnTheHerd>
#
#  This file is part of Pyroherd.
#
#  Pyroherd is free software: you can redistribute it and/or modify
#  <<<<<<< HEAD
#  =======
#  =======
#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyroherd.
#
#  Pyroherd is free software: you can redistribute it and/or modify
#  >>>>>>> 47ad949 (update)
#  >>>>>>> c723d0e (update)
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  <<<<<<< HEAD
#  Pyroherd is distributed in the hope that it will be useful,
#  =======
#  <<<<<<< HEAD
#  Pyroherd is distributed in the hope that it will be useful,
#  =======
#  Pyroherd is distributed in the hope that it will be useful,
#  >>>>>>> 47ad949 (update)
#  >>>>>>> c723d0e (update)
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  <<<<<<< HEAD
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.
#  =======
#  <<<<<<< HEAD
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.
#  =======
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.
#  >>>>>>> 47ad949 (update)
#  >>>>>>> c723d0e (update)

from io import BytesIO

from pyroherd.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyroherd.raw.core import TLObject
from pyroherd import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class WebViewResultUrl(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.WebViewResult`.

    Details:
        - Layer: ``201``
        - ID: ``4D22FF98``

    Parameters:
        url (``str``):
            N/A

        fullsize (``bool``, *optional*):
            N/A

        fullscreen (``bool``, *optional*):
            N/A

        query_id (``int`` ``64-bit``, *optional*):
            N/A

    Functions:
        This object can be returned by 4 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            messages.RequestWebView
            messages.RequestSimpleWebView
            messages.RequestAppWebView
            messages.RequestMainWebView
    """

    __slots__: List[str] = ["url", "fullsize", "fullscreen", "query_id"]

    ID = 0x4d22ff98
    QUALNAME = "types.WebViewResultUrl"

    def __init__(self, *, url: str, fullsize: Optional[bool] = None, fullscreen: Optional[bool] = None, query_id: Optional[int] = None) -> None:
        self.url = url  # string
        self.fullsize = fullsize  # flags.1?true
        self.fullscreen = fullscreen  # flags.2?true
        self.query_id = query_id  # flags.0?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "WebViewResultUrl":
        
        flags = Int.read(b)
        
        fullsize = True if flags & (1 << 1) else False
        fullscreen = True if flags & (1 << 2) else False
        query_id = Long.read(b) if flags & (1 << 0) else None
        url = String.read(b)
        
        return WebViewResultUrl(url=url, fullsize=fullsize, fullscreen=fullscreen, query_id=query_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.fullsize else 0
        flags |= (1 << 2) if self.fullscreen else 0
        flags |= (1 << 0) if self.query_id is not None else 0
        b.write(Int(flags))
        
        if self.query_id is not None:
            b.write(Long(self.query_id))
        
        b.write(String(self.url))
        
        return b.getvalue()
