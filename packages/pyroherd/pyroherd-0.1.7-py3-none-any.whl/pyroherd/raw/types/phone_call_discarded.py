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


class PhoneCallDiscarded(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.PhoneCall`.

    Details:
        - Layer: ``201``
        - ID: ``F9D25503``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        need_rating (``bool``, *optional*):
            N/A

        need_debug (``bool``, *optional*):
            N/A

        video (``bool``, *optional*):
            N/A

        reason (:obj:`PhoneCallDiscardReason <pyroherd.raw.base.PhoneCallDiscardReason>`, *optional*):
            N/A

        duration (``int`` ``32-bit``, *optional*):
            N/A

        conference_call (:obj:`InputGroupCall <pyroherd.raw.base.InputGroupCall>`, *optional*):
            N/A

    """

    __slots__: List[str] = ["id", "need_rating", "need_debug", "video", "reason", "duration", "conference_call"]

    ID = 0xf9d25503
    QUALNAME = "types.PhoneCallDiscarded"

    def __init__(self, *, id: int, need_rating: Optional[bool] = None, need_debug: Optional[bool] = None, video: Optional[bool] = None, reason: "raw.base.PhoneCallDiscardReason" = None, duration: Optional[int] = None, conference_call: "raw.base.InputGroupCall" = None) -> None:
        self.id = id  # long
        self.need_rating = need_rating  # flags.2?true
        self.need_debug = need_debug  # flags.3?true
        self.video = video  # flags.6?true
        self.reason = reason  # flags.0?PhoneCallDiscardReason
        self.duration = duration  # flags.1?int
        self.conference_call = conference_call  # flags.8?InputGroupCall

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PhoneCallDiscarded":
        
        flags = Int.read(b)
        
        need_rating = True if flags & (1 << 2) else False
        need_debug = True if flags & (1 << 3) else False
        video = True if flags & (1 << 6) else False
        id = Long.read(b)
        
        reason = TLObject.read(b) if flags & (1 << 0) else None
        
        duration = Int.read(b) if flags & (1 << 1) else None
        conference_call = TLObject.read(b) if flags & (1 << 8) else None
        
        return PhoneCallDiscarded(id=id, need_rating=need_rating, need_debug=need_debug, video=video, reason=reason, duration=duration, conference_call=conference_call)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 2) if self.need_rating else 0
        flags |= (1 << 3) if self.need_debug else 0
        flags |= (1 << 6) if self.video else 0
        flags |= (1 << 0) if self.reason is not None else 0
        flags |= (1 << 1) if self.duration is not None else 0
        flags |= (1 << 8) if self.conference_call is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.id))
        
        if self.reason is not None:
            b.write(self.reason.write())
        
        if self.duration is not None:
            b.write(Int(self.duration))
        
        if self.conference_call is not None:
            b.write(self.conference_call.write())
        
        return b.getvalue()
