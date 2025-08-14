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


class InputWebDocument(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.InputWebDocument`.

    Details:
        - Layer: ``201``
        - ID: ``9BED434D``

    Parameters:
        url (``str``):
            N/A

        size (``int`` ``32-bit``):
            N/A

        mime_type (``str``):
            N/A

        attributes (List of :obj:`DocumentAttribute <pyroherd.raw.base.DocumentAttribute>`):
            N/A

    """

    __slots__: List[str] = ["url", "size", "mime_type", "attributes"]

    ID = 0x9bed434d
    QUALNAME = "types.InputWebDocument"

    def __init__(self, *, url: str, size: int, mime_type: str, attributes: List["raw.base.DocumentAttribute"]) -> None:
        self.url = url  # string
        self.size = size  # int
        self.mime_type = mime_type  # string
        self.attributes = attributes  # Vector<DocumentAttribute>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputWebDocument":
        # No flags
        
        url = String.read(b)
        
        size = Int.read(b)
        
        mime_type = String.read(b)
        
        attributes = TLObject.read(b)
        
        return InputWebDocument(url=url, size=size, mime_type=mime_type, attributes=attributes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.url))
        
        b.write(Int(self.size))
        
        b.write(String(self.mime_type))
        
        b.write(Vector(self.attributes))
        
        return b.getvalue()
