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


class FileCdnRedirect(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.upload.File`.

    Details:
        - Layer: ``201``
        - ID: ``F18CDA44``

    Parameters:
        dc_id (``int`` ``32-bit``):
            N/A

        file_token (``bytes``):
            N/A

        encryption_key (``bytes``):
            N/A

        encryption_iv (``bytes``):
            N/A

        file_hashes (List of :obj:`FileHash <pyroherd.raw.base.FileHash>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            upload.GetFile
    """

    __slots__: List[str] = ["dc_id", "file_token", "encryption_key", "encryption_iv", "file_hashes"]

    ID = 0xf18cda44
    QUALNAME = "types.upload.FileCdnRedirect"

    def __init__(self, *, dc_id: int, file_token: bytes, encryption_key: bytes, encryption_iv: bytes, file_hashes: List["raw.base.FileHash"]) -> None:
        self.dc_id = dc_id  # int
        self.file_token = file_token  # bytes
        self.encryption_key = encryption_key  # bytes
        self.encryption_iv = encryption_iv  # bytes
        self.file_hashes = file_hashes  # Vector<FileHash>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "FileCdnRedirect":
        # No flags
        
        dc_id = Int.read(b)
        
        file_token = Bytes.read(b)
        
        encryption_key = Bytes.read(b)
        
        encryption_iv = Bytes.read(b)
        
        file_hashes = TLObject.read(b)
        
        return FileCdnRedirect(dc_id=dc_id, file_token=file_token, encryption_key=encryption_key, encryption_iv=encryption_iv, file_hashes=file_hashes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.dc_id))
        
        b.write(Bytes(self.file_token))
        
        b.write(Bytes(self.encryption_key))
        
        b.write(Bytes(self.encryption_iv))
        
        b.write(Vector(self.file_hashes))
        
        return b.getvalue()
