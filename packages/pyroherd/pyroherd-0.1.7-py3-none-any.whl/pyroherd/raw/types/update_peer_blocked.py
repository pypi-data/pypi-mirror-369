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


class UpdatePeerBlocked(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``201``
        - ID: ``EBE07752``

    Parameters:
        peer_id (:obj:`Peer <pyroherd.raw.base.Peer>`):
            N/A

        blocked (``bool``, *optional*):
            N/A

        blocked_my_stories_from (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["peer_id", "blocked", "blocked_my_stories_from"]

    ID = 0xebe07752
    QUALNAME = "types.UpdatePeerBlocked"

    def __init__(self, *, peer_id: "raw.base.Peer", blocked: Optional[bool] = None, blocked_my_stories_from: Optional[bool] = None) -> None:
        self.peer_id = peer_id  # Peer
        self.blocked = blocked  # flags.0?true
        self.blocked_my_stories_from = blocked_my_stories_from  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdatePeerBlocked":
        
        flags = Int.read(b)
        
        blocked = True if flags & (1 << 0) else False
        blocked_my_stories_from = True if flags & (1 << 1) else False
        peer_id = TLObject.read(b)
        
        return UpdatePeerBlocked(peer_id=peer_id, blocked=blocked, blocked_my_stories_from=blocked_my_stories_from)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.blocked else 0
        flags |= (1 << 1) if self.blocked_my_stories_from else 0
        b.write(Int(flags))
        
        b.write(self.peer_id.write())
        
        return b.getvalue()
