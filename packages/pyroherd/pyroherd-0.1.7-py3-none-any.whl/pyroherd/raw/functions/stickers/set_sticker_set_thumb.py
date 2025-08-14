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


class SetStickerSetThumb(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``A76A5392``

    Parameters:
        stickerset (:obj:`InputStickerSet <pyroherd.raw.base.InputStickerSet>`):
            N/A

        thumb (:obj:`InputDocument <pyroherd.raw.base.InputDocument>`, *optional*):
            N/A

        thumb_document_id (``int`` ``64-bit``, *optional*):
            N/A

    Returns:
        :obj:`messages.StickerSet <pyroherd.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["stickerset", "thumb", "thumb_document_id"]

    ID = 0xa76a5392
    QUALNAME = "functions.stickers.SetStickerSetThumb"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", thumb: "raw.base.InputDocument" = None, thumb_document_id: Optional[int] = None) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.thumb = thumb  # flags.0?InputDocument
        self.thumb_document_id = thumb_document_id  # flags.1?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetStickerSetThumb":
        
        flags = Int.read(b)
        
        stickerset = TLObject.read(b)
        
        thumb = TLObject.read(b) if flags & (1 << 0) else None
        
        thumb_document_id = Long.read(b) if flags & (1 << 1) else None
        return SetStickerSetThumb(stickerset=stickerset, thumb=thumb, thumb_document_id=thumb_document_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.thumb is not None else 0
        flags |= (1 << 1) if self.thumb_document_id is not None else 0
        b.write(Int(flags))
        
        b.write(self.stickerset.write())
        
        if self.thumb is not None:
            b.write(self.thumb.write())
        
        if self.thumb_document_id is not None:
            b.write(Long(self.thumb_document_id))
        
        return b.getvalue()
