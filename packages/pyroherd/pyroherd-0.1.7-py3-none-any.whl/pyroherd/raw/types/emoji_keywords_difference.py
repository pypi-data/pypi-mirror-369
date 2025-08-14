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


class EmojiKeywordsDifference(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.EmojiKeywordsDifference`.

    Details:
        - Layer: ``201``
        - ID: ``5CC761BD``

    Parameters:
        lang_code (``str``):
            N/A

        from_version (``int`` ``32-bit``):
            N/A

        version (``int`` ``32-bit``):
            N/A

        keywords (List of :obj:`EmojiKeyword <pyroherd.raw.base.EmojiKeyword>`):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetEmojiKeywords
            messages.GetEmojiKeywordsDifference
    """

    __slots__: List[str] = ["lang_code", "from_version", "version", "keywords"]

    ID = 0x5cc761bd
    QUALNAME = "types.EmojiKeywordsDifference"

    def __init__(self, *, lang_code: str, from_version: int, version: int, keywords: List["raw.base.EmojiKeyword"]) -> None:
        self.lang_code = lang_code  # string
        self.from_version = from_version  # int
        self.version = version  # int
        self.keywords = keywords  # Vector<EmojiKeyword>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "EmojiKeywordsDifference":
        # No flags
        
        lang_code = String.read(b)
        
        from_version = Int.read(b)
        
        version = Int.read(b)
        
        keywords = TLObject.read(b)
        
        return EmojiKeywordsDifference(lang_code=lang_code, from_version=from_version, version=version, keywords=keywords)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.lang_code))
        
        b.write(Int(self.from_version))
        
        b.write(Int(self.version))
        
        b.write(Vector(self.keywords))
        
        return b.getvalue()
