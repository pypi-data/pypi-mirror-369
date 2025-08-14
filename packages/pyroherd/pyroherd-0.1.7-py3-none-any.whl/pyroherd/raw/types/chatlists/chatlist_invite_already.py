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


class ChatlistInviteAlready(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.chatlists.ChatlistInvite`.

    Details:
        - Layer: ``201``
        - ID: ``FA87F659``

    Parameters:
        filter_id (``int`` ``32-bit``):
            N/A

        missing_peers (List of :obj:`Peer <pyroherd.raw.base.Peer>`):
            N/A

        already_peers (List of :obj:`Peer <pyroherd.raw.base.Peer>`):
            N/A

        chats (List of :obj:`Chat <pyroherd.raw.base.Chat>`):
            N/A

        users (List of :obj:`User <pyroherd.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            chatlists.CheckChatlistInvite
    """

    __slots__: List[str] = ["filter_id", "missing_peers", "already_peers", "chats", "users"]

    ID = 0xfa87f659
    QUALNAME = "types.chatlists.ChatlistInviteAlready"

    def __init__(self, *, filter_id: int, missing_peers: List["raw.base.Peer"], already_peers: List["raw.base.Peer"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.filter_id = filter_id  # int
        self.missing_peers = missing_peers  # Vector<Peer>
        self.already_peers = already_peers  # Vector<Peer>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatlistInviteAlready":
        # No flags
        
        filter_id = Int.read(b)
        
        missing_peers = TLObject.read(b)
        
        already_peers = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ChatlistInviteAlready(filter_id=filter_id, missing_peers=missing_peers, already_peers=already_peers, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.filter_id))
        
        b.write(Vector(self.missing_peers))
        
        b.write(Vector(self.already_peers))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
