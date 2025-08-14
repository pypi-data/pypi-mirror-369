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


class UploadWallPaper(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``E39A8F03``

    Parameters:
        file (:obj:`InputFile <pyroherd.raw.base.InputFile>`):
            N/A

        mime_type (``str``):
            N/A

        settings (:obj:`WallPaperSettings <pyroherd.raw.base.WallPaperSettings>`):
            N/A

        for_chat (``bool``, *optional*):
            N/A

    Returns:
        :obj:`WallPaper <pyroherd.raw.base.WallPaper>`
    """

    __slots__: List[str] = ["file", "mime_type", "settings", "for_chat"]

    ID = 0xe39a8f03
    QUALNAME = "functions.account.UploadWallPaper"

    def __init__(self, *, file: "raw.base.InputFile", mime_type: str, settings: "raw.base.WallPaperSettings", for_chat: Optional[bool] = None) -> None:
        self.file = file  # InputFile
        self.mime_type = mime_type  # string
        self.settings = settings  # WallPaperSettings
        self.for_chat = for_chat  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UploadWallPaper":
        
        flags = Int.read(b)
        
        for_chat = True if flags & (1 << 0) else False
        file = TLObject.read(b)
        
        mime_type = String.read(b)
        
        settings = TLObject.read(b)
        
        return UploadWallPaper(file=file, mime_type=mime_type, settings=settings, for_chat=for_chat)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.for_chat else 0
        b.write(Int(flags))
        
        b.write(self.file.write())
        
        b.write(String(self.mime_type))
        
        b.write(self.settings.write())
        
        return b.getvalue()
