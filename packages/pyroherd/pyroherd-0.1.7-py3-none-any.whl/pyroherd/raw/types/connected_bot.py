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


class ConnectedBot(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.ConnectedBot`.

    Details:
        - Layer: ``201``
        - ID: ``CD64636C``

    Parameters:
        bot_id (``int`` ``64-bit``):
            N/A

        recipients (:obj:`BusinessBotRecipients <pyroherd.raw.base.BusinessBotRecipients>`):
            N/A

        rights (:obj:`BusinessBotRights <pyroherd.raw.base.BusinessBotRights>`):
            N/A

    """

    __slots__: List[str] = ["bot_id", "recipients", "rights"]

    ID = 0xcd64636c
    QUALNAME = "types.ConnectedBot"

    def __init__(self, *, bot_id: int, recipients: "raw.base.BusinessBotRecipients", rights: "raw.base.BusinessBotRights") -> None:
        self.bot_id = bot_id  # long
        self.recipients = recipients  # BusinessBotRecipients
        self.rights = rights  # BusinessBotRights

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ConnectedBot":
        
        flags = Int.read(b)
        
        bot_id = Long.read(b)
        
        recipients = TLObject.read(b)
        
        rights = TLObject.read(b)
        
        return ConnectedBot(bot_id=bot_id, recipients=recipients, rights=rights)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        
        b.write(Int(flags))
        
        b.write(Long(self.bot_id))
        
        b.write(self.recipients.write())
        
        b.write(self.rights.write())
        
        return b.getvalue()
