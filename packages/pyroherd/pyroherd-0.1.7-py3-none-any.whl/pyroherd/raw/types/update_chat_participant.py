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


class UpdateChatParticipant(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``201``
        - ID: ``D087663A``

    Parameters:
        chat_id (``int`` ``64-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

        actor_id (``int`` ``64-bit``):
            N/A

        user_id (``int`` ``64-bit``):
            N/A

        qts (``int`` ``32-bit``):
            N/A

        prev_participant (:obj:`ChatParticipant <pyroherd.raw.base.ChatParticipant>`, *optional*):
            N/A

        new_participant (:obj:`ChatParticipant <pyroherd.raw.base.ChatParticipant>`, *optional*):
            N/A

        invite (:obj:`ExportedChatInvite <pyroherd.raw.base.ExportedChatInvite>`, *optional*):
            N/A

    """

    __slots__: List[str] = ["chat_id", "date", "actor_id", "user_id", "qts", "prev_participant", "new_participant", "invite"]

    ID = 0xd087663a
    QUALNAME = "types.UpdateChatParticipant"

    def __init__(self, *, chat_id: int, date: int, actor_id: int, user_id: int, qts: int, prev_participant: "raw.base.ChatParticipant" = None, new_participant: "raw.base.ChatParticipant" = None, invite: "raw.base.ExportedChatInvite" = None) -> None:
        self.chat_id = chat_id  # long
        self.date = date  # int
        self.actor_id = actor_id  # long
        self.user_id = user_id  # long
        self.qts = qts  # int
        self.prev_participant = prev_participant  # flags.0?ChatParticipant
        self.new_participant = new_participant  # flags.1?ChatParticipant
        self.invite = invite  # flags.2?ExportedChatInvite

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateChatParticipant":
        
        flags = Int.read(b)
        
        chat_id = Long.read(b)
        
        date = Int.read(b)
        
        actor_id = Long.read(b)
        
        user_id = Long.read(b)
        
        prev_participant = TLObject.read(b) if flags & (1 << 0) else None
        
        new_participant = TLObject.read(b) if flags & (1 << 1) else None
        
        invite = TLObject.read(b) if flags & (1 << 2) else None
        
        qts = Int.read(b)
        
        return UpdateChatParticipant(chat_id=chat_id, date=date, actor_id=actor_id, user_id=user_id, qts=qts, prev_participant=prev_participant, new_participant=new_participant, invite=invite)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.prev_participant is not None else 0
        flags |= (1 << 1) if self.new_participant is not None else 0
        flags |= (1 << 2) if self.invite is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.chat_id))
        
        b.write(Int(self.date))
        
        b.write(Long(self.actor_id))
        
        b.write(Long(self.user_id))
        
        if self.prev_participant is not None:
            b.write(self.prev_participant.write())
        
        if self.new_participant is not None:
            b.write(self.new_participant.write())
        
        if self.invite is not None:
            b.write(self.invite.write())
        
        b.write(Int(self.qts))
        
        return b.getvalue()
