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


class GetChatInviteImporters(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``DF04DD4E``

    Parameters:
        peer (:obj:`InputPeer <pyroherd.raw.base.InputPeer>`):
            N/A

        offset_date (``int`` ``32-bit``):
            N/A

        offset_user (:obj:`InputUser <pyroherd.raw.base.InputUser>`):
            N/A

        limit (``int`` ``32-bit``):
            N/A

        requested (``bool``, *optional*):
            N/A

        subscription_expired (``bool``, *optional*):
            N/A

        link (``str``, *optional*):
            N/A

        q (``str``, *optional*):
            N/A

    Returns:
        :obj:`messages.ChatInviteImporters <pyroherd.raw.base.messages.ChatInviteImporters>`
    """

    __slots__: List[str] = ["peer", "offset_date", "offset_user", "limit", "requested", "subscription_expired", "link", "q"]

    ID = 0xdf04dd4e
    QUALNAME = "functions.messages.GetChatInviteImporters"

    def __init__(self, *, peer: "raw.base.InputPeer", offset_date: int, offset_user: "raw.base.InputUser", limit: int, requested: Optional[bool] = None, subscription_expired: Optional[bool] = None, link: Optional[str] = None, q: Optional[str] = None) -> None:
        self.peer = peer  # InputPeer
        self.offset_date = offset_date  # int
        self.offset_user = offset_user  # InputUser
        self.limit = limit  # int
        self.requested = requested  # flags.0?true
        self.subscription_expired = subscription_expired  # flags.3?true
        self.link = link  # flags.1?string
        self.q = q  # flags.2?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetChatInviteImporters":
        
        flags = Int.read(b)
        
        requested = True if flags & (1 << 0) else False
        subscription_expired = True if flags & (1 << 3) else False
        peer = TLObject.read(b)
        
        link = String.read(b) if flags & (1 << 1) else None
        q = String.read(b) if flags & (1 << 2) else None
        offset_date = Int.read(b)
        
        offset_user = TLObject.read(b)
        
        limit = Int.read(b)
        
        return GetChatInviteImporters(peer=peer, offset_date=offset_date, offset_user=offset_user, limit=limit, requested=requested, subscription_expired=subscription_expired, link=link, q=q)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.requested else 0
        flags |= (1 << 3) if self.subscription_expired else 0
        flags |= (1 << 1) if self.link is not None else 0
        flags |= (1 << 2) if self.q is not None else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        if self.link is not None:
            b.write(String(self.link))
        
        if self.q is not None:
            b.write(String(self.q))
        
        b.write(Int(self.offset_date))
        
        b.write(self.offset_user.write())
        
        b.write(Int(self.limit))
        
        return b.getvalue()
