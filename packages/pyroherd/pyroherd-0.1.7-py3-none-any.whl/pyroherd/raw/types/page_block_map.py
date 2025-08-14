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


class PageBlockMap(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.PageBlock`.

    Details:
        - Layer: ``201``
        - ID: ``A44F3EF6``

    Parameters:
        geo (:obj:`GeoPoint <pyroherd.raw.base.GeoPoint>`):
            N/A

        zoom (``int`` ``32-bit``):
            N/A

        w (``int`` ``32-bit``):
            N/A

        h (``int`` ``32-bit``):
            N/A

        caption (:obj:`PageCaption <pyroherd.raw.base.PageCaption>`):
            N/A

    """

    __slots__: List[str] = ["geo", "zoom", "w", "h", "caption"]

    ID = 0xa44f3ef6
    QUALNAME = "types.PageBlockMap"

    def __init__(self, *, geo: "raw.base.GeoPoint", zoom: int, w: int, h: int, caption: "raw.base.PageCaption") -> None:
        self.geo = geo  # GeoPoint
        self.zoom = zoom  # int
        self.w = w  # int
        self.h = h  # int
        self.caption = caption  # PageCaption

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PageBlockMap":
        # No flags
        
        geo = TLObject.read(b)
        
        zoom = Int.read(b)
        
        w = Int.read(b)
        
        h = Int.read(b)
        
        caption = TLObject.read(b)
        
        return PageBlockMap(geo=geo, zoom=zoom, w=w, h=h, caption=caption)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.geo.write())
        
        b.write(Int(self.zoom))
        
        b.write(Int(self.w))
        
        b.write(Int(self.h))
        
        b.write(self.caption.write())
        
        return b.getvalue()
