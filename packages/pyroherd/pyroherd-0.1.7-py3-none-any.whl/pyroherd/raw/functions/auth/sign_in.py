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


class SignIn(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``8D52A951``

    Parameters:
        phone_number (``str``):
            N/A

        phone_code_hash (``str``):
            N/A

        phone_code (``str``, *optional*):
            N/A

        email_verification (:obj:`EmailVerification <pyroherd.raw.base.EmailVerification>`, *optional*):
            N/A

    Returns:
        :obj:`auth.Authorization <pyroherd.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["phone_number", "phone_code_hash", "phone_code", "email_verification"]

    ID = 0x8d52a951
    QUALNAME = "functions.auth.SignIn"

    def __init__(self, *, phone_number: str, phone_code_hash: str, phone_code: Optional[str] = None, email_verification: "raw.base.EmailVerification" = None) -> None:
        self.phone_number = phone_number  # string
        self.phone_code_hash = phone_code_hash  # string
        self.phone_code = phone_code  # flags.0?string
        self.email_verification = email_verification  # flags.1?EmailVerification

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SignIn":
        
        flags = Int.read(b)
        
        phone_number = String.read(b)
        
        phone_code_hash = String.read(b)
        
        phone_code = String.read(b) if flags & (1 << 0) else None
        email_verification = TLObject.read(b) if flags & (1 << 1) else None
        
        return SignIn(phone_number=phone_number, phone_code_hash=phone_code_hash, phone_code=phone_code, email_verification=email_verification)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.phone_code is not None else 0
        flags |= (1 << 1) if self.email_verification is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.phone_number))
        
        b.write(String(self.phone_code_hash))
        
        if self.phone_code is not None:
            b.write(String(self.phone_code))
        
        if self.email_verification is not None:
            b.write(self.email_verification.write())
        
        return b.getvalue()
