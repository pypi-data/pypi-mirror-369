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


class BotVerifierSettings(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.BotVerifierSettings`.

    Details:
        - Layer: ``201``
        - ID: ``B0CD6617``

    Parameters:
        icon (``int`` ``64-bit``):
            N/A

        company (``str``):
            N/A

        can_modify_custom_description (``bool``, *optional*):
            N/A

        custom_description (``str``, *optional*):
            N/A

    """

    __slots__: List[str] = ["icon", "company", "can_modify_custom_description", "custom_description"]

    ID = 0xb0cd6617
    QUALNAME = "types.BotVerifierSettings"

    def __init__(self, *, icon: int, company: str, can_modify_custom_description: Optional[bool] = None, custom_description: Optional[str] = None) -> None:
        self.icon = icon  # long
        self.company = company  # string
        self.can_modify_custom_description = can_modify_custom_description  # flags.1?true
        self.custom_description = custom_description  # flags.0?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BotVerifierSettings":
        
        flags = Int.read(b)
        
        can_modify_custom_description = True if flags & (1 << 1) else False
        icon = Long.read(b)
        
        company = String.read(b)
        
        custom_description = String.read(b) if flags & (1 << 0) else None
        return BotVerifierSettings(icon=icon, company=company, can_modify_custom_description=can_modify_custom_description, custom_description=custom_description)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.can_modify_custom_description else 0
        flags |= (1 << 0) if self.custom_description is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.icon))
        
        b.write(String(self.company))
        
        if self.custom_description is not None:
            b.write(String(self.custom_description))
        
        return b.getvalue()
