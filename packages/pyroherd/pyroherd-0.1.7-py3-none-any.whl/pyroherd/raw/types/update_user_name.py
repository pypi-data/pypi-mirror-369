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


class UpdateUserName(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``201``
        - ID: ``A7848924``

    Parameters:
        user_id (``int`` ``64-bit``):
            N/A

        first_name (``str``):
            N/A

        last_name (``str``):
            N/A

        usernames (List of :obj:`Username <pyroherd.raw.base.Username>`):
            N/A

    """

    __slots__: List[str] = ["user_id", "first_name", "last_name", "usernames"]

    ID = 0xa7848924
    QUALNAME = "types.UpdateUserName"

    def __init__(self, *, user_id: int, first_name: str, last_name: str, usernames: List["raw.base.Username"]) -> None:
        self.user_id = user_id  # long
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.usernames = usernames  # Vector<Username>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateUserName":
        # No flags
        
        user_id = Long.read(b)
        
        first_name = String.read(b)
        
        last_name = String.read(b)
        
        usernames = TLObject.read(b)
        
        return UpdateUserName(user_id=user_id, first_name=first_name, last_name=last_name, usernames=usernames)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.user_id))
        
        b.write(String(self.first_name))
        
        b.write(String(self.last_name))
        
        b.write(Vector(self.usernames))
        
        return b.getvalue()
