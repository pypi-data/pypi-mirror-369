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


class FeaturedStickers(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.messages.FeaturedStickers`.

    Details:
        - Layer: ``201``
        - ID: ``BE382906``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        count (``int`` ``32-bit``):
            N/A

        sets (List of :obj:`StickerSetCovered <pyroherd.raw.base.StickerSetCovered>`):
            N/A

        unread (List of ``int`` ``64-bit``):
            N/A

        premium (``bool``, *optional*):
            N/A

    Functions:
        This object can be returned by 3 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetFeaturedStickers
            messages.GetOldFeaturedStickers
            messages.GetFeaturedEmojiStickers
    """

    __slots__: List[str] = ["hash", "count", "sets", "unread", "premium"]

    ID = 0xbe382906
    QUALNAME = "types.messages.FeaturedStickers"

    def __init__(self, *, hash: int, count: int, sets: List["raw.base.StickerSetCovered"], unread: List[int], premium: Optional[bool] = None) -> None:
        self.hash = hash  # long
        self.count = count  # int
        self.sets = sets  # Vector<StickerSetCovered>
        self.unread = unread  # Vector<long>
        self.premium = premium  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "FeaturedStickers":
        
        flags = Int.read(b)
        
        premium = True if flags & (1 << 0) else False
        hash = Long.read(b)
        
        count = Int.read(b)
        
        sets = TLObject.read(b)
        
        unread = TLObject.read(b, Long)
        
        return FeaturedStickers(hash=hash, count=count, sets=sets, unread=unread, premium=premium)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.premium else 0
        b.write(Int(flags))
        
        b.write(Long(self.hash))
        
        b.write(Int(self.count))
        
        b.write(Vector(self.sets))
        
        b.write(Vector(self.unread, Long))
        
        return b.getvalue()
