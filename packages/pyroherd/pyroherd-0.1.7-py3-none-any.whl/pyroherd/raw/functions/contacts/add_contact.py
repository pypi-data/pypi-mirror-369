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


class AddContact(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``E8F463D0``

    Parameters:
        id (:obj:`InputUser <pyroherd.raw.base.InputUser>`):
            N/A

        first_name (``str``):
            N/A

        last_name (``str``):
            N/A

        phone (``str``):
            N/A

        add_phone_privacy_exception (``bool``, *optional*):
            N/A

    Returns:
        :obj:`Updates <pyroherd.raw.base.Updates>`
    """

    __slots__: List[str] = ["id", "first_name", "last_name", "phone", "add_phone_privacy_exception"]

    ID = 0xe8f463d0
    QUALNAME = "functions.contacts.AddContact"

    def __init__(self, *, id: "raw.base.InputUser", first_name: str, last_name: str, phone: str, add_phone_privacy_exception: Optional[bool] = None) -> None:
        self.id = id  # InputUser
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.phone = phone  # string
        self.add_phone_privacy_exception = add_phone_privacy_exception  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AddContact":
        
        flags = Int.read(b)
        
        add_phone_privacy_exception = True if flags & (1 << 0) else False
        id = TLObject.read(b)
        
        first_name = String.read(b)
        
        last_name = String.read(b)
        
        phone = String.read(b)
        
        return AddContact(id=id, first_name=first_name, last_name=last_name, phone=phone, add_phone_privacy_exception=add_phone_privacy_exception)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.add_phone_privacy_exception else 0
        b.write(Int(flags))
        
        b.write(self.id.write())
        
        b.write(String(self.first_name))
        
        b.write(String(self.last_name))
        
        b.write(String(self.phone))
        
        return b.getvalue()
