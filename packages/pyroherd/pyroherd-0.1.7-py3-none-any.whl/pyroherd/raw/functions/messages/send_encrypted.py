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


class SendEncrypted(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``44FA7A15``

    Parameters:
        peer (:obj:`InputEncryptedChat <pyroherd.raw.base.InputEncryptedChat>`):
            N/A

        random_id (``int`` ``64-bit``):
            N/A

        data (``bytes``):
            N/A

        silent (``bool``, *optional*):
            N/A

    Returns:
        :obj:`messages.SentEncryptedMessage <pyroherd.raw.base.messages.SentEncryptedMessage>`
    """

    __slots__: List[str] = ["peer", "random_id", "data", "silent"]

    ID = 0x44fa7a15
    QUALNAME = "functions.messages.SendEncrypted"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", random_id: int, data: bytes, silent: Optional[bool] = None) -> None:
        self.peer = peer  # InputEncryptedChat
        self.random_id = random_id  # long
        self.data = data  # bytes
        self.silent = silent  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendEncrypted":
        
        flags = Int.read(b)
        
        silent = True if flags & (1 << 0) else False
        peer = TLObject.read(b)
        
        random_id = Long.read(b)
        
        data = Bytes.read(b)
        
        return SendEncrypted(peer=peer, random_id=random_id, data=data, silent=silent)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.silent else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Long(self.random_id))
        
        b.write(Bytes(self.data))
        
        return b.getvalue()
