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


class SearchPosts(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``D1810907``

    Parameters:
        offset (``str``):
            N/A

        limit (``int`` ``32-bit``):
            N/A

        hashtag (``str``, *optional*):
            N/A

        area (:obj:`MediaArea <pyroherd.raw.base.MediaArea>`, *optional*):
            N/A

        peer (:obj:`InputPeer <pyroherd.raw.base.InputPeer>`, *optional*):
            N/A

    Returns:
        :obj:`stories.FoundStories <pyroherd.raw.base.stories.FoundStories>`
    """

    __slots__: List[str] = ["offset", "limit", "hashtag", "area", "peer"]

    ID = 0xd1810907
    QUALNAME = "functions.stories.SearchPosts"

    def __init__(self, *, offset: str, limit: int, hashtag: Optional[str] = None, area: "raw.base.MediaArea" = None, peer: "raw.base.InputPeer" = None) -> None:
        self.offset = offset  # string
        self.limit = limit  # int
        self.hashtag = hashtag  # flags.0?string
        self.area = area  # flags.1?MediaArea
        self.peer = peer  # flags.2?InputPeer

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SearchPosts":
        
        flags = Int.read(b)
        
        hashtag = String.read(b) if flags & (1 << 0) else None
        area = TLObject.read(b) if flags & (1 << 1) else None
        
        peer = TLObject.read(b) if flags & (1 << 2) else None
        
        offset = String.read(b)
        
        limit = Int.read(b)
        
        return SearchPosts(offset=offset, limit=limit, hashtag=hashtag, area=area, peer=peer)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.hashtag is not None else 0
        flags |= (1 << 1) if self.area is not None else 0
        flags |= (1 << 2) if self.peer is not None else 0
        b.write(Int(flags))
        
        if self.hashtag is not None:
            b.write(String(self.hashtag))
        
        if self.area is not None:
            b.write(self.area.write())
        
        if self.peer is not None:
            b.write(self.peer.write())
        
        b.write(String(self.offset))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
