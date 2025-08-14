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


class WallPaper(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.WallPaper`.

    Details:
        - Layer: ``201``
        - ID: ``A437C3ED``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        access_hash (``int`` ``64-bit``):
            N/A

        slug (``str``):
            N/A

        document (:obj:`Document <pyroherd.raw.base.Document>`):
            N/A

        creator (``bool``, *optional*):
            N/A

        default (``bool``, *optional*):
            N/A

        pattern (``bool``, *optional*):
            N/A

        dark (``bool``, *optional*):
            N/A

        settings (:obj:`WallPaperSettings <pyroherd.raw.base.WallPaperSettings>`, *optional*):
            N/A

    Functions:
        This object can be returned by 3 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetWallPaper
            account.UploadWallPaper
            account.GetMultiWallPapers
    """

    __slots__: List[str] = ["id", "access_hash", "slug", "document", "creator", "default", "pattern", "dark", "settings"]

    ID = 0xa437c3ed
    QUALNAME = "types.WallPaper"

    def __init__(self, *, id: int, access_hash: int, slug: str, document: "raw.base.Document", creator: Optional[bool] = None, default: Optional[bool] = None, pattern: Optional[bool] = None, dark: Optional[bool] = None, settings: "raw.base.WallPaperSettings" = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.slug = slug  # string
        self.document = document  # Document
        self.creator = creator  # flags.0?true
        self.default = default  # flags.1?true
        self.pattern = pattern  # flags.3?true
        self.dark = dark  # flags.4?true
        self.settings = settings  # flags.2?WallPaperSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "WallPaper":
        
        id = Long.read(b)
        
        flags = Int.read(b)
        
        creator = True if flags & (1 << 0) else False
        default = True if flags & (1 << 1) else False
        pattern = True if flags & (1 << 3) else False
        dark = True if flags & (1 << 4) else False
        access_hash = Long.read(b)
        
        slug = String.read(b)
        
        document = TLObject.read(b)
        
        settings = TLObject.read(b) if flags & (1 << 2) else None
        
        return WallPaper(id=id, access_hash=access_hash, slug=slug, document=document, creator=creator, default=default, pattern=pattern, dark=dark, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        
        b.write(Long(self.id))
        flags = 0
        flags |= (1 << 0) if self.creator else 0
        flags |= (1 << 1) if self.default else 0
        flags |= (1 << 3) if self.pattern else 0
        flags |= (1 << 4) if self.dark else 0
        flags |= (1 << 2) if self.settings is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.access_hash))
        
        b.write(String(self.slug))
        
        b.write(self.document.write())
        
        if self.settings is not None:
            b.write(self.settings.write())
        
        return b.getvalue()
