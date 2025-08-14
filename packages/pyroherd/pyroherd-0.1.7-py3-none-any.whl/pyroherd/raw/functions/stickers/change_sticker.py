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


class ChangeSticker(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``F5537EBC``

    Parameters:
        sticker (:obj:`InputDocument <pyroherd.raw.base.InputDocument>`):
            N/A

        emoji (``str``, *optional*):
            N/A

        mask_coords (:obj:`MaskCoords <pyroherd.raw.base.MaskCoords>`, *optional*):
            N/A

        keywords (``str``, *optional*):
            N/A

    Returns:
        :obj:`messages.StickerSet <pyroherd.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["sticker", "emoji", "mask_coords", "keywords"]

    ID = 0xf5537ebc
    QUALNAME = "functions.stickers.ChangeSticker"

    def __init__(self, *, sticker: "raw.base.InputDocument", emoji: Optional[str] = None, mask_coords: "raw.base.MaskCoords" = None, keywords: Optional[str] = None) -> None:
        self.sticker = sticker  # InputDocument
        self.emoji = emoji  # flags.0?string
        self.mask_coords = mask_coords  # flags.1?MaskCoords
        self.keywords = keywords  # flags.2?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChangeSticker":
        
        flags = Int.read(b)
        
        sticker = TLObject.read(b)
        
        emoji = String.read(b) if flags & (1 << 0) else None
        mask_coords = TLObject.read(b) if flags & (1 << 1) else None
        
        keywords = String.read(b) if flags & (1 << 2) else None
        return ChangeSticker(sticker=sticker, emoji=emoji, mask_coords=mask_coords, keywords=keywords)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.emoji is not None else 0
        flags |= (1 << 1) if self.mask_coords is not None else 0
        flags |= (1 << 2) if self.keywords is not None else 0
        b.write(Int(flags))
        
        b.write(self.sticker.write())
        
        if self.emoji is not None:
            b.write(String(self.emoji))
        
        if self.mask_coords is not None:
            b.write(self.mask_coords.write())
        
        if self.keywords is not None:
            b.write(String(self.keywords))
        
        return b.getvalue()
