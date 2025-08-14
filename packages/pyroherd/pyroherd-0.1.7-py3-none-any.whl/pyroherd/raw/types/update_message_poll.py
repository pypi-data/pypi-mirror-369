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


class UpdateMessagePoll(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``201``
        - ID: ``ACA1657B``

    Parameters:
        poll_id (``int`` ``64-bit``):
            N/A

        results (:obj:`PollResults <pyroherd.raw.base.PollResults>`):
            N/A

        poll (:obj:`Poll <pyroherd.raw.base.Poll>`, *optional*):
            N/A

    """

    __slots__: List[str] = ["poll_id", "results", "poll"]

    ID = 0xaca1657b
    QUALNAME = "types.UpdateMessagePoll"

    def __init__(self, *, poll_id: int, results: "raw.base.PollResults", poll: "raw.base.Poll" = None) -> None:
        self.poll_id = poll_id  # long
        self.results = results  # PollResults
        self.poll = poll  # flags.0?Poll

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateMessagePoll":
        
        flags = Int.read(b)
        
        poll_id = Long.read(b)
        
        poll = TLObject.read(b) if flags & (1 << 0) else None
        
        results = TLObject.read(b)
        
        return UpdateMessagePoll(poll_id=poll_id, results=results, poll=poll)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.poll is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.poll_id))
        
        if self.poll is not None:
            b.write(self.poll.write())
        
        b.write(self.results.write())
        
        return b.getvalue()
