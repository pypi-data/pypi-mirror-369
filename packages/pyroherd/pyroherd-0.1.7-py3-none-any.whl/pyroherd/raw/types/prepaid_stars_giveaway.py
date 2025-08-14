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


class PrepaidStarsGiveaway(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.PrepaidGiveaway`.

    Details:
        - Layer: ``201``
        - ID: ``9A9D77E0``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        stars (``int`` ``64-bit``):
            N/A

        quantity (``int`` ``32-bit``):
            N/A

        boosts (``int`` ``32-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["id", "stars", "quantity", "boosts", "date"]

    ID = 0x9a9d77e0
    QUALNAME = "types.PrepaidStarsGiveaway"

    def __init__(self, *, id: int, stars: int, quantity: int, boosts: int, date: int) -> None:
        self.id = id  # long
        self.stars = stars  # long
        self.quantity = quantity  # int
        self.boosts = boosts  # int
        self.date = date  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PrepaidStarsGiveaway":
        # No flags
        
        id = Long.read(b)
        
        stars = Long.read(b)
        
        quantity = Int.read(b)
        
        boosts = Int.read(b)
        
        date = Int.read(b)
        
        return PrepaidStarsGiveaway(id=id, stars=stars, quantity=quantity, boosts=boosts, date=date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.id))
        
        b.write(Long(self.stars))
        
        b.write(Int(self.quantity))
        
        b.write(Int(self.boosts))
        
        b.write(Int(self.date))
        
        return b.getvalue()
