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


class GetSuggestedStarRefBots(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``D6B48F7``

    Parameters:
        peer (:obj:`InputPeer <pyroherd.raw.base.InputPeer>`):
            N/A

        offset (``str``):
            N/A

        limit (``int`` ``32-bit``):
            N/A

        order_by_revenue (``bool``, *optional*):
            N/A

        order_by_date (``bool``, *optional*):
            N/A

    Returns:
        :obj:`payments.SuggestedStarRefBots <pyroherd.raw.base.payments.SuggestedStarRefBots>`
    """

    __slots__: List[str] = ["peer", "offset", "limit", "order_by_revenue", "order_by_date"]

    ID = 0xd6b48f7
    QUALNAME = "functions.payments.GetSuggestedStarRefBots"

    def __init__(self, *, peer: "raw.base.InputPeer", offset: str, limit: int, order_by_revenue: Optional[bool] = None, order_by_date: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.offset = offset  # string
        self.limit = limit  # int
        self.order_by_revenue = order_by_revenue  # flags.0?true
        self.order_by_date = order_by_date  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetSuggestedStarRefBots":
        
        flags = Int.read(b)
        
        order_by_revenue = True if flags & (1 << 0) else False
        order_by_date = True if flags & (1 << 1) else False
        peer = TLObject.read(b)
        
        offset = String.read(b)
        
        limit = Int.read(b)
        
        return GetSuggestedStarRefBots(peer=peer, offset=offset, limit=limit, order_by_revenue=order_by_revenue, order_by_date=order_by_date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.order_by_revenue else 0
        flags |= (1 << 1) if self.order_by_date else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(String(self.offset))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
