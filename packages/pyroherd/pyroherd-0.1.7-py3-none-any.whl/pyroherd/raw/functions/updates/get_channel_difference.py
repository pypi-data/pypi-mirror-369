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


class GetChannelDifference(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``3173D78``

    Parameters:
        channel (:obj:`InputChannel <pyroherd.raw.base.InputChannel>`):
            N/A

        filter (:obj:`ChannelMessagesFilter <pyroherd.raw.base.ChannelMessagesFilter>`):
            N/A

        pts (``int`` ``32-bit``):
            N/A

        limit (``int`` ``32-bit``):
            N/A

        force (``bool``, *optional*):
            N/A

    Returns:
        :obj:`updates.ChannelDifference <pyroherd.raw.base.updates.ChannelDifference>`
    """

    __slots__: List[str] = ["channel", "filter", "pts", "limit", "force"]

    ID = 0x3173d78
    QUALNAME = "functions.updates.GetChannelDifference"

    def __init__(self, *, channel: "raw.base.InputChannel", filter: "raw.base.ChannelMessagesFilter", pts: int, limit: int, force: Optional[bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.filter = filter  # ChannelMessagesFilter
        self.pts = pts  # int
        self.limit = limit  # int
        self.force = force  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetChannelDifference":
        
        flags = Int.read(b)
        
        force = True if flags & (1 << 0) else False
        channel = TLObject.read(b)
        
        filter = TLObject.read(b)
        
        pts = Int.read(b)
        
        limit = Int.read(b)
        
        return GetChannelDifference(channel=channel, filter=filter, pts=pts, limit=limit, force=force)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.force else 0
        b.write(Int(flags))
        
        b.write(self.channel.write())
        
        b.write(self.filter.write())
        
        b.write(Int(self.pts))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
