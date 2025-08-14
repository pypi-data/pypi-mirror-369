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


class AccessPointRule(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.AccessPointRule`.

    Details:
        - Layer: ``201``
        - ID: ``4679B65F``

    Parameters:
        phone_prefix_rules (``str``):
            N/A

        dc_id (``int`` ``32-bit``):
            N/A

        ips (List of :obj:`IpPort <pyroherd.raw.base.IpPort>`):
            N/A

    """

    __slots__: List[str] = ["phone_prefix_rules", "dc_id", "ips"]

    ID = 0x4679b65f
    QUALNAME = "types.AccessPointRule"

    def __init__(self, *, phone_prefix_rules: str, dc_id: int, ips: List["raw.base.IpPort"]) -> None:
        self.phone_prefix_rules = phone_prefix_rules  # string
        self.dc_id = dc_id  # int
        self.ips = ips  # vector<IpPort>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AccessPointRule":
        # No flags
        
        phone_prefix_rules = String.read(b)
        
        dc_id = Int.read(b)
        
        ips = TLObject.read(b)
        
        return AccessPointRule(phone_prefix_rules=phone_prefix_rules, dc_id=dc_id, ips=ips)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.phone_prefix_rules))
        
        b.write(Int(self.dc_id))
        
        b.write(Vector(self.ips))
        
        return b.getvalue()
