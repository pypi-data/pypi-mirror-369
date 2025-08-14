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


class GroupCallParticipantVideo(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.GroupCallParticipantVideo`.

    Details:
        - Layer: ``201``
        - ID: ``67753AC8``

    Parameters:
        endpoint (``str``):
            N/A

        source_groups (List of :obj:`GroupCallParticipantVideoSourceGroup <pyroherd.raw.base.GroupCallParticipantVideoSourceGroup>`):
            N/A

        paused (``bool``, *optional*):
            N/A

        audio_source (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["endpoint", "source_groups", "paused", "audio_source"]

    ID = 0x67753ac8
    QUALNAME = "types.GroupCallParticipantVideo"

    def __init__(self, *, endpoint: str, source_groups: List["raw.base.GroupCallParticipantVideoSourceGroup"], paused: Optional[bool] = None, audio_source: Optional[int] = None) -> None:
        self.endpoint = endpoint  # string
        self.source_groups = source_groups  # Vector<GroupCallParticipantVideoSourceGroup>
        self.paused = paused  # flags.0?true
        self.audio_source = audio_source  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GroupCallParticipantVideo":
        
        flags = Int.read(b)
        
        paused = True if flags & (1 << 0) else False
        endpoint = String.read(b)
        
        source_groups = TLObject.read(b)
        
        audio_source = Int.read(b) if flags & (1 << 1) else None
        return GroupCallParticipantVideo(endpoint=endpoint, source_groups=source_groups, paused=paused, audio_source=audio_source)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.paused else 0
        flags |= (1 << 1) if self.audio_source is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.endpoint))
        
        b.write(Vector(self.source_groups))
        
        if self.audio_source is not None:
            b.write(Int(self.audio_source))
        
        return b.getvalue()
