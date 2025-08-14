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


class MessageActionSetChatWallPaper(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.MessageAction`.

    Details:
        - Layer: ``201``
        - ID: ``5060A3F4``

    Parameters:
        wallpaper (:obj:`WallPaper <pyroherd.raw.base.WallPaper>`):
            N/A

        same (``bool``, *optional*):
            N/A

        for_both (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["wallpaper", "same", "for_both"]

    ID = 0x5060a3f4
    QUALNAME = "types.MessageActionSetChatWallPaper"

    def __init__(self, *, wallpaper: "raw.base.WallPaper", same: Optional[bool] = None, for_both: Optional[bool] = None) -> None:
        self.wallpaper = wallpaper  # WallPaper
        self.same = same  # flags.0?true
        self.for_both = for_both  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionSetChatWallPaper":
        
        flags = Int.read(b)
        
        same = True if flags & (1 << 0) else False
        for_both = True if flags & (1 << 1) else False
        wallpaper = TLObject.read(b)
        
        return MessageActionSetChatWallPaper(wallpaper=wallpaper, same=same, for_both=for_both)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.same else 0
        flags |= (1 << 1) if self.for_both else 0
        b.write(Int(flags))
        
        b.write(self.wallpaper.write())
        
        return b.getvalue()
