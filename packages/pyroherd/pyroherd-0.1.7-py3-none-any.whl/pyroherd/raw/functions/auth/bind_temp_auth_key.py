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


class BindTempAuthKey(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``CDD42A05``

    Parameters:
        perm_auth_key_id (``int`` ``64-bit``):
            N/A

        nonce (``int`` ``64-bit``):
            N/A

        expires_at (``int`` ``32-bit``):
            N/A

        encrypted_message (``bytes``):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["perm_auth_key_id", "nonce", "expires_at", "encrypted_message"]

    ID = 0xcdd42a05
    QUALNAME = "functions.auth.BindTempAuthKey"

    def __init__(self, *, perm_auth_key_id: int, nonce: int, expires_at: int, encrypted_message: bytes) -> None:
        self.perm_auth_key_id = perm_auth_key_id  # long
        self.nonce = nonce  # long
        self.expires_at = expires_at  # int
        self.encrypted_message = encrypted_message  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BindTempAuthKey":
        # No flags
        
        perm_auth_key_id = Long.read(b)
        
        nonce = Long.read(b)
        
        expires_at = Int.read(b)
        
        encrypted_message = Bytes.read(b)
        
        return BindTempAuthKey(perm_auth_key_id=perm_auth_key_id, nonce=nonce, expires_at=expires_at, encrypted_message=encrypted_message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.perm_auth_key_id))
        
        b.write(Long(self.nonce))
        
        b.write(Int(self.expires_at))
        
        b.write(Bytes(self.encrypted_message))
        
        return b.getvalue()
