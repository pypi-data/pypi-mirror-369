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


class EncryptedMessageService(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.EncryptedMessage`.

    Details:
        - Layer: ``201``
        - ID: ``23734B06``

    Parameters:
        random_id (``int`` ``64-bit``):
            N/A

        chat_id (``int`` ``32-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

        bytes (``bytes``):
            N/A

    """

    __slots__: List[str] = ["random_id", "chat_id", "date", "bytes"]

    ID = 0x23734b06
    QUALNAME = "types.EncryptedMessageService"

    def __init__(self, *, random_id: int, chat_id: int, date: int, bytes: bytes) -> None:
        self.random_id = random_id  # long
        self.chat_id = chat_id  # int
        self.date = date  # int
        self.bytes = bytes  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "EncryptedMessageService":
        # No flags
        
        random_id = Long.read(b)
        
        chat_id = Int.read(b)
        
        date = Int.read(b)
        
        bytes = Bytes.read(b)
        
        return EncryptedMessageService(random_id=random_id, chat_id=chat_id, date=date, bytes=bytes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.random_id))
        
        b.write(Int(self.chat_id))
        
        b.write(Int(self.date))
        
        b.write(Bytes(self.bytes))
        
        return b.getvalue()
