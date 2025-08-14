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


class UploadTheme(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``1C3DB333``

    Parameters:
        file (:obj:`InputFile <pyroherd.raw.base.InputFile>`):
            N/A

        file_name (``str``):
            N/A

        mime_type (``str``):
            N/A

        thumb (:obj:`InputFile <pyroherd.raw.base.InputFile>`, *optional*):
            N/A

    Returns:
        :obj:`Document <pyroherd.raw.base.Document>`
    """

    __slots__: List[str] = ["file", "file_name", "mime_type", "thumb"]

    ID = 0x1c3db333
    QUALNAME = "functions.account.UploadTheme"

    def __init__(self, *, file: "raw.base.InputFile", file_name: str, mime_type: str, thumb: "raw.base.InputFile" = None) -> None:
        self.file = file  # InputFile
        self.file_name = file_name  # string
        self.mime_type = mime_type  # string
        self.thumb = thumb  # flags.0?InputFile

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UploadTheme":
        
        flags = Int.read(b)
        
        file = TLObject.read(b)
        
        thumb = TLObject.read(b) if flags & (1 << 0) else None
        
        file_name = String.read(b)
        
        mime_type = String.read(b)
        
        return UploadTheme(file=file, file_name=file_name, mime_type=mime_type, thumb=thumb)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.thumb is not None else 0
        b.write(Int(flags))
        
        b.write(self.file.write())
        
        if self.thumb is not None:
            b.write(self.thumb.write())
        
        b.write(String(self.file_name))
        
        b.write(String(self.mime_type))
        
        return b.getvalue()
