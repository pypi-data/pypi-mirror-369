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


class ChannelParticipant(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.ChannelParticipant`.

    Details:
        - Layer: ``201``
        - ID: ``CB397619``

    Parameters:
        user_id (``int`` ``64-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

        subscription_until_date (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["user_id", "date", "subscription_until_date"]

    ID = 0xcb397619
    QUALNAME = "types.ChannelParticipant"

    def __init__(self, *, user_id: int, date: int, subscription_until_date: Optional[int] = None) -> None:
        self.user_id = user_id  # long
        self.date = date  # int
        self.subscription_until_date = subscription_until_date  # flags.0?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelParticipant":
        
        flags = Int.read(b)
        
        user_id = Long.read(b)
        
        date = Int.read(b)
        
        subscription_until_date = Int.read(b) if flags & (1 << 0) else None
        return ChannelParticipant(user_id=user_id, date=date, subscription_until_date=subscription_until_date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.subscription_until_date is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.user_id))
        
        b.write(Int(self.date))
        
        if self.subscription_until_date is not None:
            b.write(Int(self.subscription_until_date))
        
        return b.getvalue()
