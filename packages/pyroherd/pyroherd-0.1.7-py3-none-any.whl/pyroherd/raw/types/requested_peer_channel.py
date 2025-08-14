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


class RequestedPeerChannel(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.RequestedPeer`.

    Details:
        - Layer: ``201``
        - ID: ``8BA403E4``

    Parameters:
        channel_id (``int`` ``64-bit``):
            N/A

        title (``str``, *optional*):
            N/A

        username (``str``, *optional*):
            N/A

        photo (:obj:`Photo <pyroherd.raw.base.Photo>`, *optional*):
            N/A

    """

    __slots__: List[str] = ["channel_id", "title", "username", "photo"]

    ID = 0x8ba403e4
    QUALNAME = "types.RequestedPeerChannel"

    def __init__(self, *, channel_id: int, title: Optional[str] = None, username: Optional[str] = None, photo: "raw.base.Photo" = None) -> None:
        self.channel_id = channel_id  # long
        self.title = title  # flags.0?string
        self.username = username  # flags.1?string
        self.photo = photo  # flags.2?Photo

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "RequestedPeerChannel":
        
        flags = Int.read(b)
        
        channel_id = Long.read(b)
        
        title = String.read(b) if flags & (1 << 0) else None
        username = String.read(b) if flags & (1 << 1) else None
        photo = TLObject.read(b) if flags & (1 << 2) else None
        
        return RequestedPeerChannel(channel_id=channel_id, title=title, username=username, photo=photo)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.username is not None else 0
        flags |= (1 << 2) if self.photo is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.channel_id))
        
        if self.title is not None:
            b.write(String(self.title))
        
        if self.username is not None:
            b.write(String(self.username))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        return b.getvalue()
