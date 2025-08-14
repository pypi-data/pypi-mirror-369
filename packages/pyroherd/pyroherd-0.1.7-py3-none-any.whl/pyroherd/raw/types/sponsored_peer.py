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


class SponsoredPeer(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.SponsoredPeer`.

    Details:
        - Layer: ``201``
        - ID: ``C69708D3``

    Parameters:
        random_id (``bytes``):
            N/A

        peer (:obj:`Peer <pyroherd.raw.base.Peer>`):
            N/A

        sponsor_info (``str``, *optional*):
            N/A

        additional_info (``str``, *optional*):
            N/A

    """

    __slots__: List[str] = ["random_id", "peer", "sponsor_info", "additional_info"]

    ID = 0xc69708d3
    QUALNAME = "types.SponsoredPeer"

    def __init__(self, *, random_id: bytes, peer: "raw.base.Peer", sponsor_info: Optional[str] = None, additional_info: Optional[str] = None) -> None:
        self.random_id = random_id  # bytes
        self.peer = peer  # Peer
        self.sponsor_info = sponsor_info  # flags.0?string
        self.additional_info = additional_info  # flags.1?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SponsoredPeer":
        
        flags = Int.read(b)
        
        random_id = Bytes.read(b)
        
        peer = TLObject.read(b)
        
        sponsor_info = String.read(b) if flags & (1 << 0) else None
        additional_info = String.read(b) if flags & (1 << 1) else None
        return SponsoredPeer(random_id=random_id, peer=peer, sponsor_info=sponsor_info, additional_info=additional_info)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.sponsor_info is not None else 0
        flags |= (1 << 1) if self.additional_info is not None else 0
        b.write(Int(flags))
        
        b.write(Bytes(self.random_id))
        
        b.write(self.peer.write())
        
        if self.sponsor_info is not None:
            b.write(String(self.sponsor_info))
        
        if self.additional_info is not None:
            b.write(String(self.additional_info))
        
        return b.getvalue()
