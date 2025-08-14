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


class UrlAuthResultRequest(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.UrlAuthResult`.

    Details:
        - Layer: ``201``
        - ID: ``92D33A0E``

    Parameters:
        bot (:obj:`User <pyroherd.raw.base.User>`):
            N/A

        domain (``str``):
            N/A

        request_write_access (``bool``, *optional*):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            messages.RequestUrlAuth
            messages.AcceptUrlAuth
    """

    __slots__: List[str] = ["bot", "domain", "request_write_access"]

    ID = 0x92d33a0e
    QUALNAME = "types.UrlAuthResultRequest"

    def __init__(self, *, bot: "raw.base.User", domain: str, request_write_access: Optional[bool] = None) -> None:
        self.bot = bot  # User
        self.domain = domain  # string
        self.request_write_access = request_write_access  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UrlAuthResultRequest":
        
        flags = Int.read(b)
        
        request_write_access = True if flags & (1 << 0) else False
        bot = TLObject.read(b)
        
        domain = String.read(b)
        
        return UrlAuthResultRequest(bot=bot, domain=domain, request_write_access=request_write_access)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.request_write_access else 0
        b.write(Int(flags))
        
        b.write(self.bot.write())
        
        b.write(String(self.domain))
        
        return b.getvalue()
