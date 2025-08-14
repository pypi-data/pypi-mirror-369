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


class InputPhotoLegacyFileLocation(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.InputFileLocation`.

    Details:
        - Layer: ``201``
        - ID: ``D83466F3``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        access_hash (``int`` ``64-bit``):
            N/A

        file_reference (``bytes``):
            N/A

        volume_id (``int`` ``64-bit``):
            N/A

        local_id (``int`` ``32-bit``):
            N/A

        secret (``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["id", "access_hash", "file_reference", "volume_id", "local_id", "secret"]

    ID = 0xd83466f3
    QUALNAME = "types.InputPhotoLegacyFileLocation"

    def __init__(self, *, id: int, access_hash: int, file_reference: bytes, volume_id: int, local_id: int, secret: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.file_reference = file_reference  # bytes
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.secret = secret  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputPhotoLegacyFileLocation":
        # No flags
        
        id = Long.read(b)
        
        access_hash = Long.read(b)
        
        file_reference = Bytes.read(b)
        
        volume_id = Long.read(b)
        
        local_id = Int.read(b)
        
        secret = Long.read(b)
        
        return InputPhotoLegacyFileLocation(id=id, access_hash=access_hash, file_reference=file_reference, volume_id=volume_id, local_id=local_id, secret=secret)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.id))
        
        b.write(Long(self.access_hash))
        
        b.write(Bytes(self.file_reference))
        
        b.write(Long(self.volume_id))
        
        b.write(Int(self.local_id))
        
        b.write(Long(self.secret))
        
        return b.getvalue()
