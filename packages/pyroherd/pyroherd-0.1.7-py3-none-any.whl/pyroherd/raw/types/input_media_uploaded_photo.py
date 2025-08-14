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


class InputMediaUploadedPhoto(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.InputMedia`.

    Details:
        - Layer: ``201``
        - ID: ``1E287D04``

    Parameters:
        file (:obj:`InputFile <pyroherd.raw.base.InputFile>`):
            N/A

        spoiler (``bool``, *optional*):
            N/A

        stickers (List of :obj:`InputDocument <pyroherd.raw.base.InputDocument>`, *optional*):
            N/A

        ttl_seconds (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["file", "spoiler", "stickers", "ttl_seconds"]

    ID = 0x1e287d04
    QUALNAME = "types.InputMediaUploadedPhoto"

    def __init__(self, *, file: "raw.base.InputFile", spoiler: Optional[bool] = None, stickers: Optional[List["raw.base.InputDocument"]] = None, ttl_seconds: Optional[int] = None) -> None:
        self.file = file  # InputFile
        self.spoiler = spoiler  # flags.2?true
        self.stickers = stickers  # flags.0?Vector<InputDocument>
        self.ttl_seconds = ttl_seconds  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputMediaUploadedPhoto":
        
        flags = Int.read(b)
        
        spoiler = True if flags & (1 << 2) else False
        file = TLObject.read(b)
        
        stickers = TLObject.read(b) if flags & (1 << 0) else []
        
        ttl_seconds = Int.read(b) if flags & (1 << 1) else None
        return InputMediaUploadedPhoto(file=file, spoiler=spoiler, stickers=stickers, ttl_seconds=ttl_seconds)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 2) if self.spoiler else 0
        flags |= (1 << 0) if self.stickers else 0
        flags |= (1 << 1) if self.ttl_seconds is not None else 0
        b.write(Int(flags))
        
        b.write(self.file.write())
        
        if self.stickers is not None:
            b.write(Vector(self.stickers))
        
        if self.ttl_seconds is not None:
            b.write(Int(self.ttl_seconds))
        
        return b.getvalue()
