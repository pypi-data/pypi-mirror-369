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


class GroupCall(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.phone.GroupCall`.

    Details:
        - Layer: ``201``
        - ID: ``9E727AAD``

    Parameters:
        call (:obj:`GroupCall <pyroherd.raw.base.GroupCall>`):
            N/A

        participants (List of :obj:`GroupCallParticipant <pyroherd.raw.base.GroupCallParticipant>`):
            N/A

        participants_next_offset (``str``):
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

            phone.GetGroupCall
    """

    __slots__: List[str] = ["call", "participants", "participants_next_offset", "chats", "users"]

    ID = 0x9e727aad
    QUALNAME = "types.phone.GroupCall"

    def __init__(self, *, call: "raw.base.GroupCall", participants: List["raw.base.GroupCallParticipant"], participants_next_offset: str, chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.call = call  # GroupCall
        self.participants = participants  # Vector<GroupCallParticipant>
        self.participants_next_offset = participants_next_offset  # string
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GroupCall":
        # No flags
        
        call = TLObject.read(b)
        
        participants = TLObject.read(b)
        
        participants_next_offset = String.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return GroupCall(call=call, participants=participants, participants_next_offset=participants_next_offset, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(Vector(self.participants))
        
        b.write(String(self.participants_next_offset))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
