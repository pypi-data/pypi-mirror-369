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


class UpdateDeleteScheduledMessages(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``201``
        - ID: ``F2A71983``

    Parameters:
        peer (:obj:`Peer <pyroherd.raw.base.Peer>`):
            N/A

        messages (List of ``int`` ``32-bit``):
            N/A

        sent_messages (List of ``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["peer", "messages", "sent_messages"]

    ID = 0xf2a71983
    QUALNAME = "types.UpdateDeleteScheduledMessages"

    def __init__(self, *, peer: "raw.base.Peer", messages: List[int], sent_messages: Optional[List[int]] = None) -> None:
        self.peer = peer  # Peer
        self.messages = messages  # Vector<int>
        self.sent_messages = sent_messages  # flags.0?Vector<int>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateDeleteScheduledMessages":
        
        flags = Int.read(b)
        
        peer = TLObject.read(b)
        
        messages = TLObject.read(b, Int)
        
        sent_messages = TLObject.read(b, Int) if flags & (1 << 0) else []
        
        return UpdateDeleteScheduledMessages(peer=peer, messages=messages, sent_messages=sent_messages)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.sent_messages else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Vector(self.messages, Int))
        
        if self.sent_messages is not None:
            b.write(Vector(self.sent_messages, Int))
        
        return b.getvalue()
