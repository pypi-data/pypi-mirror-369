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


class PreparedInlineMessage(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.messages.PreparedInlineMessage`.

    Details:
        - Layer: ``201``
        - ID: ``FF57708D``

    Parameters:
        query_id (``int`` ``64-bit``):
            N/A

        result (:obj:`BotInlineResult <pyroherd.raw.base.BotInlineResult>`):
            N/A

        peer_types (List of :obj:`InlineQueryPeerType <pyroherd.raw.base.InlineQueryPeerType>`):
            N/A

        cache_time (``int`` ``32-bit``):
            N/A

        users (List of :obj:`User <pyroherd.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetPreparedInlineMessage
    """

    __slots__: List[str] = ["query_id", "result", "peer_types", "cache_time", "users"]

    ID = 0xff57708d
    QUALNAME = "types.messages.PreparedInlineMessage"

    def __init__(self, *, query_id: int, result: "raw.base.BotInlineResult", peer_types: List["raw.base.InlineQueryPeerType"], cache_time: int, users: List["raw.base.User"]) -> None:
        self.query_id = query_id  # long
        self.result = result  # BotInlineResult
        self.peer_types = peer_types  # Vector<InlineQueryPeerType>
        self.cache_time = cache_time  # int
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PreparedInlineMessage":
        # No flags
        
        query_id = Long.read(b)
        
        result = TLObject.read(b)
        
        peer_types = TLObject.read(b)
        
        cache_time = Int.read(b)
        
        users = TLObject.read(b)
        
        return PreparedInlineMessage(query_id=query_id, result=result, peer_types=peer_types, cache_time=cache_time, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.query_id))
        
        b.write(self.result.write())
        
        b.write(Vector(self.peer_types))
        
        b.write(Int(self.cache_time))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
