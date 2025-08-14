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


class UpdateReadHistoryInbox(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``201``
        - ID: ``9C974FDF``

    Parameters:
        peer (:obj:`Peer <pyroherd.raw.base.Peer>`):
            N/A

        max_id (``int`` ``32-bit``):
            N/A

        still_unread_count (``int`` ``32-bit``):
            N/A

        pts (``int`` ``32-bit``):
            N/A

        pts_count (``int`` ``32-bit``):
            N/A

        folder_id (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["peer", "max_id", "still_unread_count", "pts", "pts_count", "folder_id"]

    ID = 0x9c974fdf
    QUALNAME = "types.UpdateReadHistoryInbox"

    def __init__(self, *, peer: "raw.base.Peer", max_id: int, still_unread_count: int, pts: int, pts_count: int, folder_id: Optional[int] = None) -> None:
        self.peer = peer  # Peer
        self.max_id = max_id  # int
        self.still_unread_count = still_unread_count  # int
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.folder_id = folder_id  # flags.0?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateReadHistoryInbox":
        
        flags = Int.read(b)
        
        folder_id = Int.read(b) if flags & (1 << 0) else None
        peer = TLObject.read(b)
        
        max_id = Int.read(b)
        
        still_unread_count = Int.read(b)
        
        pts = Int.read(b)
        
        pts_count = Int.read(b)
        
        return UpdateReadHistoryInbox(peer=peer, max_id=max_id, still_unread_count=still_unread_count, pts=pts, pts_count=pts_count, folder_id=folder_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.folder_id is not None else 0
        b.write(Int(flags))
        
        if self.folder_id is not None:
            b.write(Int(self.folder_id))
        
        b.write(self.peer.write())
        
        b.write(Int(self.max_id))
        
        b.write(Int(self.still_unread_count))
        
        b.write(Int(self.pts))
        
        b.write(Int(self.pts_count))
        
        return b.getvalue()
