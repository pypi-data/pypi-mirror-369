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


class ChangeAuthorizationSettings(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``40F48462``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        confirmed (``bool``, *optional*):
            N/A

        encrypted_requests_disabled (``bool``, *optional*):
            N/A

        call_requests_disabled (``bool``, *optional*):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["hash", "confirmed", "encrypted_requests_disabled", "call_requests_disabled"]

    ID = 0x40f48462
    QUALNAME = "functions.account.ChangeAuthorizationSettings"

    def __init__(self, *, hash: int, confirmed: Optional[bool] = None, encrypted_requests_disabled: Optional[bool] = None, call_requests_disabled: Optional[bool] = None) -> None:
        self.hash = hash  # long
        self.confirmed = confirmed  # flags.3?true
        self.encrypted_requests_disabled = encrypted_requests_disabled  # flags.0?Bool
        self.call_requests_disabled = call_requests_disabled  # flags.1?Bool

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChangeAuthorizationSettings":
        
        flags = Int.read(b)
        
        confirmed = True if flags & (1 << 3) else False
        hash = Long.read(b)
        
        encrypted_requests_disabled = Bool.read(b) if flags & (1 << 0) else None
        call_requests_disabled = Bool.read(b) if flags & (1 << 1) else None
        return ChangeAuthorizationSettings(hash=hash, confirmed=confirmed, encrypted_requests_disabled=encrypted_requests_disabled, call_requests_disabled=call_requests_disabled)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 3) if self.confirmed else 0
        flags |= (1 << 0) if self.encrypted_requests_disabled is not None else 0
        flags |= (1 << 1) if self.call_requests_disabled is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.hash))
        
        if self.encrypted_requests_disabled is not None:
            b.write(Bool(self.encrypted_requests_disabled))
        
        if self.call_requests_disabled is not None:
            b.write(Bool(self.call_requests_disabled))
        
        return b.getvalue()
