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


class SavePreparedInlineMessage(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``F21F7F2F``

    Parameters:
        result (:obj:`InputBotInlineResult <pyroherd.raw.base.InputBotInlineResult>`):
            N/A

        user_id (:obj:`InputUser <pyroherd.raw.base.InputUser>`):
            N/A

        peer_types (List of :obj:`InlineQueryPeerType <pyroherd.raw.base.InlineQueryPeerType>`, *optional*):
            N/A

    Returns:
        :obj:`messages.BotPreparedInlineMessage <pyroherd.raw.base.messages.BotPreparedInlineMessage>`
    """

    __slots__: List[str] = ["result", "user_id", "peer_types"]

    ID = 0xf21f7f2f
    QUALNAME = "functions.messages.SavePreparedInlineMessage"

    def __init__(self, *, result: "raw.base.InputBotInlineResult", user_id: "raw.base.InputUser", peer_types: Optional[List["raw.base.InlineQueryPeerType"]] = None) -> None:
        self.result = result  # InputBotInlineResult
        self.user_id = user_id  # InputUser
        self.peer_types = peer_types  # flags.0?Vector<InlineQueryPeerType>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SavePreparedInlineMessage":
        
        flags = Int.read(b)
        
        result = TLObject.read(b)
        
        user_id = TLObject.read(b)
        
        peer_types = TLObject.read(b) if flags & (1 << 0) else []
        
        return SavePreparedInlineMessage(result=result, user_id=user_id, peer_types=peer_types)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.peer_types else 0
        b.write(Int(flags))
        
        b.write(self.result.write())
        
        b.write(self.user_id.write())
        
        if self.peer_types is not None:
            b.write(Vector(self.peer_types))
        
        return b.getvalue()
