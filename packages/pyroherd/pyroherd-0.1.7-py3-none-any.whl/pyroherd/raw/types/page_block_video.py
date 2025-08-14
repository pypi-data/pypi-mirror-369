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


class PageBlockVideo(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.PageBlock`.

    Details:
        - Layer: ``201``
        - ID: ``7C8FE7B6``

    Parameters:
        video_id (``int`` ``64-bit``):
            N/A

        caption (:obj:`PageCaption <pyroherd.raw.base.PageCaption>`):
            N/A

        autoplay (``bool``, *optional*):
            N/A

        loop (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["video_id", "caption", "autoplay", "loop"]

    ID = 0x7c8fe7b6
    QUALNAME = "types.PageBlockVideo"

    def __init__(self, *, video_id: int, caption: "raw.base.PageCaption", autoplay: Optional[bool] = None, loop: Optional[bool] = None) -> None:
        self.video_id = video_id  # long
        self.caption = caption  # PageCaption
        self.autoplay = autoplay  # flags.0?true
        self.loop = loop  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PageBlockVideo":
        
        flags = Int.read(b)
        
        autoplay = True if flags & (1 << 0) else False
        loop = True if flags & (1 << 1) else False
        video_id = Long.read(b)
        
        caption = TLObject.read(b)
        
        return PageBlockVideo(video_id=video_id, caption=caption, autoplay=autoplay, loop=loop)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.autoplay else 0
        flags |= (1 << 1) if self.loop else 0
        b.write(Int(flags))
        
        b.write(Long(self.video_id))
        
        b.write(self.caption.write())
        
        return b.getvalue()
