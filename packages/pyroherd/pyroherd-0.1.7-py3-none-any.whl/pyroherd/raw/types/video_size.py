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


class VideoSize(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.VideoSize`.

    Details:
        - Layer: ``201``
        - ID: ``DE33B094``

    Parameters:
        type (``str``):
            N/A

        w (``int`` ``32-bit``):
            N/A

        h (``int`` ``32-bit``):
            N/A

        size (``int`` ``32-bit``):
            N/A

        video_start_ts (``float`` ``64-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["type", "w", "h", "size", "video_start_ts"]

    ID = 0xde33b094
    QUALNAME = "types.VideoSize"

    def __init__(self, *, type: str, w: int, h: int, size: int, video_start_ts: Optional[float] = None) -> None:
        self.type = type  # string
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.video_start_ts = video_start_ts  # flags.0?double

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "VideoSize":
        
        flags = Int.read(b)
        
        type = String.read(b)
        
        w = Int.read(b)
        
        h = Int.read(b)
        
        size = Int.read(b)
        
        video_start_ts = Double.read(b) if flags & (1 << 0) else None
        return VideoSize(type=type, w=w, h=h, size=size, video_start_ts=video_start_ts)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.video_start_ts is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.type))
        
        b.write(Int(self.w))
        
        b.write(Int(self.h))
        
        b.write(Int(self.size))
        
        if self.video_start_ts is not None:
            b.write(Double(self.video_start_ts))
        
        return b.getvalue()
