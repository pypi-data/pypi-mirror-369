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


class StarsGiveawayWinnersOption(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.StarsGiveawayWinnersOption`.

    Details:
        - Layer: ``201``
        - ID: ``54236209``

    Parameters:
        users (``int`` ``32-bit``):
            N/A

        per_user_stars (``int`` ``64-bit``):
            N/A

        default (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["users", "per_user_stars", "default"]

    ID = 0x54236209
    QUALNAME = "types.StarsGiveawayWinnersOption"

    def __init__(self, *, users: int, per_user_stars: int, default: Optional[bool] = None) -> None:
        self.users = users  # int
        self.per_user_stars = per_user_stars  # long
        self.default = default  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarsGiveawayWinnersOption":
        
        flags = Int.read(b)
        
        default = True if flags & (1 << 0) else False
        users = Int.read(b)
        
        per_user_stars = Long.read(b)
        
        return StarsGiveawayWinnersOption(users=users, per_user_stars=per_user_stars, default=default)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.default else 0
        b.write(Int(flags))
        
        b.write(Int(self.users))
        
        b.write(Long(self.per_user_stars))
        
        return b.getvalue()
