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


class ChannelAdminLogEventActionEditMessage(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``201``
        - ID: ``709B2405``

    Parameters:
        prev_message (:obj:`Message <pyroherd.raw.base.Message>`):
            N/A

        new_message (:obj:`Message <pyroherd.raw.base.Message>`):
            N/A

    """

    __slots__: List[str] = ["prev_message", "new_message"]

    ID = 0x709b2405
    QUALNAME = "types.ChannelAdminLogEventActionEditMessage"

    def __init__(self, *, prev_message: "raw.base.Message", new_message: "raw.base.Message") -> None:
        self.prev_message = prev_message  # Message
        self.new_message = new_message  # Message

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionEditMessage":
        # No flags
        
        prev_message = TLObject.read(b)
        
        new_message = TLObject.read(b)
        
        return ChannelAdminLogEventActionEditMessage(prev_message=prev_message, new_message=new_message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.prev_message.write())
        
        b.write(self.new_message.write())
        
        return b.getvalue()
