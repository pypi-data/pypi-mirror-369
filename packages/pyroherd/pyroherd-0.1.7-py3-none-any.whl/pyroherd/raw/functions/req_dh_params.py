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


class ReqDHParams(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``D712E4BE``

    Parameters:
        nonce (``int`` ``128-bit``):
            N/A

        server_nonce (``int`` ``128-bit``):
            N/A

        p (``bytes``):
            N/A

        q (``bytes``):
            N/A

        public_key_fingerprint (``int`` ``64-bit``):
            N/A

        encrypted_data (``bytes``):
            N/A

    Returns:
        :obj:`ServerDHParams <pyroherd.raw.base.ServerDHParams>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "p", "q", "public_key_fingerprint", "encrypted_data"]

    ID = 0xd712e4be
    QUALNAME = "functions.ReqDHParams"

    def __init__(self, *, nonce: int, server_nonce: int, p: bytes, q: bytes, public_key_fingerprint: int, encrypted_data: bytes) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.p = p  # bytes
        self.q = q  # bytes
        self.public_key_fingerprint = public_key_fingerprint  # long
        self.encrypted_data = encrypted_data  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReqDHParams":
        # No flags
        
        nonce = Int128.read(b)
        
        server_nonce = Int128.read(b)
        
        p = Bytes.read(b)
        
        q = Bytes.read(b)
        
        public_key_fingerprint = Long.read(b)
        
        encrypted_data = Bytes.read(b)
        
        return ReqDHParams(nonce=nonce, server_nonce=server_nonce, p=p, q=q, public_key_fingerprint=public_key_fingerprint, encrypted_data=encrypted_data)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int128(self.nonce))
        
        b.write(Int128(self.server_nonce))
        
        b.write(Bytes(self.p))
        
        b.write(Bytes(self.q))
        
        b.write(Long(self.public_key_fingerprint))
        
        b.write(Bytes(self.encrypted_data))
        
        return b.getvalue()
