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


class BusinessAwayMessage(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.BusinessAwayMessage`.

    Details:
        - Layer: ``201``
        - ID: ``EF156A5C``

    Parameters:
        shortcut_id (``int`` ``32-bit``):
            N/A

        schedule (:obj:`BusinessAwayMessageSchedule <pyroherd.raw.base.BusinessAwayMessageSchedule>`):
            N/A

        recipients (:obj:`BusinessRecipients <pyroherd.raw.base.BusinessRecipients>`):
            N/A

        offline_only (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["shortcut_id", "schedule", "recipients", "offline_only"]

    ID = 0xef156a5c
    QUALNAME = "types.BusinessAwayMessage"

    def __init__(self, *, shortcut_id: int, schedule: "raw.base.BusinessAwayMessageSchedule", recipients: "raw.base.BusinessRecipients", offline_only: Optional[bool] = None) -> None:
        self.shortcut_id = shortcut_id  # int
        self.schedule = schedule  # BusinessAwayMessageSchedule
        self.recipients = recipients  # BusinessRecipients
        self.offline_only = offline_only  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BusinessAwayMessage":
        
        flags = Int.read(b)
        
        offline_only = True if flags & (1 << 0) else False
        shortcut_id = Int.read(b)
        
        schedule = TLObject.read(b)
        
        recipients = TLObject.read(b)
        
        return BusinessAwayMessage(shortcut_id=shortcut_id, schedule=schedule, recipients=recipients, offline_only=offline_only)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.offline_only else 0
        b.write(Int(flags))
        
        b.write(Int(self.shortcut_id))
        
        b.write(self.schedule.write())
        
        b.write(self.recipients.write())
        
        return b.getvalue()
