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


class ImportBotAuthorization(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``67A3FF2C``

    Parameters:
        flags (``int`` ``32-bit``):
            N/A

        api_id (``int`` ``32-bit``):
            N/A

        api_hash (``str``):
            N/A

        bot_auth_token (``str``):
            N/A

    Returns:
        :obj:`auth.Authorization <pyroherd.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["flags", "api_id", "api_hash", "bot_auth_token"]

    ID = 0x67a3ff2c
    QUALNAME = "functions.auth.ImportBotAuthorization"

    def __init__(self, *, flags: int, api_id: int, api_hash: str, bot_auth_token: str) -> None:
        self.flags = flags  # int
        self.api_id = api_id  # int
        self.api_hash = api_hash  # string
        self.bot_auth_token = bot_auth_token  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ImportBotAuthorization":
        # No flags
        
        flags = Int.read(b)
        
        api_id = Int.read(b)
        
        api_hash = String.read(b)
        
        bot_auth_token = String.read(b)
        
        return ImportBotAuthorization(flags=flags, api_id=api_id, api_hash=api_hash, bot_auth_token=bot_auth_token)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.flags))
        
        b.write(Int(self.api_id))
        
        b.write(String(self.api_hash))
        
        b.write(String(self.bot_auth_token))
        
        return b.getvalue()
