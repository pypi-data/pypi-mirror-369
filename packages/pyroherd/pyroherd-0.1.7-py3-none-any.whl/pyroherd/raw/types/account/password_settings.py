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


class PasswordSettings(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.account.PasswordSettings`.

    Details:
        - Layer: ``201``
        - ID: ``9A5C33E5``

    Parameters:
        email (``str``, *optional*):
            N/A

        secure_settings (:obj:`SecureSecretSettings <pyroherd.raw.base.SecureSecretSettings>`, *optional*):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetPasswordSettings
    """

    __slots__: List[str] = ["email", "secure_settings"]

    ID = 0x9a5c33e5
    QUALNAME = "types.account.PasswordSettings"

    def __init__(self, *, email: Optional[str] = None, secure_settings: "raw.base.SecureSecretSettings" = None) -> None:
        self.email = email  # flags.0?string
        self.secure_settings = secure_settings  # flags.1?SecureSecretSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PasswordSettings":
        
        flags = Int.read(b)
        
        email = String.read(b) if flags & (1 << 0) else None
        secure_settings = TLObject.read(b) if flags & (1 << 1) else None
        
        return PasswordSettings(email=email, secure_settings=secure_settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.email is not None else 0
        flags |= (1 << 1) if self.secure_settings is not None else 0
        b.write(Int(flags))
        
        if self.email is not None:
            b.write(String(self.email))
        
        if self.secure_settings is not None:
            b.write(self.secure_settings.write())
        
        return b.getvalue()
