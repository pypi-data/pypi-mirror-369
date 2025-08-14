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


class StickerSet(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.messages.StickerSet`.

    Details:
        - Layer: ``201``
        - ID: ``6E153F16``

    Parameters:
        set (:obj:`StickerSet <pyroherd.raw.base.StickerSet>`):
            N/A

        packs (List of :obj:`StickerPack <pyroherd.raw.base.StickerPack>`):
            N/A

        keywords (List of :obj:`StickerKeyword <pyroherd.raw.base.StickerKeyword>`):
            N/A

        documents (List of :obj:`Document <pyroherd.raw.base.Document>`):
            N/A

    Functions:
        This object can be returned by 9 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetStickerSet
            stickers.CreateStickerSet
            stickers.RemoveStickerFromSet
            stickers.ChangeStickerPosition
            stickers.AddStickerToSet
            stickers.SetStickerSetThumb
            stickers.ChangeSticker
            stickers.RenameStickerSet
            stickers.ReplaceSticker
    """

    __slots__: List[str] = ["set", "packs", "keywords", "documents"]

    ID = 0x6e153f16
    QUALNAME = "types.messages.StickerSet"

    def __init__(self, *, set: "raw.base.StickerSet", packs: List["raw.base.StickerPack"], keywords: List["raw.base.StickerKeyword"], documents: List["raw.base.Document"]) -> None:
        self.set = set  # StickerSet
        self.packs = packs  # Vector<StickerPack>
        self.keywords = keywords  # Vector<StickerKeyword>
        self.documents = documents  # Vector<Document>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StickerSet":
        # No flags
        
        set = TLObject.read(b)
        
        packs = TLObject.read(b)
        
        keywords = TLObject.read(b)
        
        documents = TLObject.read(b)
        
        return StickerSet(set=set, packs=packs, keywords=keywords, documents=documents)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.set.write())
        
        b.write(Vector(self.packs))
        
        b.write(Vector(self.keywords))
        
        b.write(Vector(self.documents))
        
        return b.getvalue()
