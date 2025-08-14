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


class BindAuthKeyInner(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.BindAuthKeyInner`.

    Details:
        - Layer: ``201``
        - ID: ``75A3F765``

    Parameters:
        nonce (``int`` ``64-bit``):
            N/A

        temp_auth_key_id (``int`` ``64-bit``):
            N/A

        perm_auth_key_id (``int`` ``64-bit``):
            N/A

        temp_session_id (``int`` ``64-bit``):
            N/A

        expires_at (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["nonce", "temp_auth_key_id", "perm_auth_key_id", "temp_session_id", "expires_at"]

    ID = 0x75a3f765
    QUALNAME = "types.BindAuthKeyInner"

    def __init__(self, *, nonce: int, temp_auth_key_id: int, perm_auth_key_id: int, temp_session_id: int, expires_at: int) -> None:
        self.nonce = nonce  # long
        self.temp_auth_key_id = temp_auth_key_id  # long
        self.perm_auth_key_id = perm_auth_key_id  # long
        self.temp_session_id = temp_session_id  # long
        self.expires_at = expires_at  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BindAuthKeyInner":
        # No flags
        
        nonce = Long.read(b)
        
        temp_auth_key_id = Long.read(b)
        
        perm_auth_key_id = Long.read(b)
        
        temp_session_id = Long.read(b)
        
        expires_at = Int.read(b)
        
        return BindAuthKeyInner(nonce=nonce, temp_auth_key_id=temp_auth_key_id, perm_auth_key_id=perm_auth_key_id, temp_session_id=temp_session_id, expires_at=expires_at)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.nonce))
        
        b.write(Long(self.temp_auth_key_id))
        
        b.write(Long(self.perm_auth_key_id))
        
        b.write(Long(self.temp_session_id))
        
        b.write(Int(self.expires_at))
        
        return b.getvalue()
