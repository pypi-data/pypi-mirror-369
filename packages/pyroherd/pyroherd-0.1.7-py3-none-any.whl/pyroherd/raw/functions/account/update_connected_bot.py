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


class UpdateConnectedBot(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``66A08C7E``

    Parameters:
        bot (:obj:`InputUser <pyroherd.raw.base.InputUser>`):
            N/A

        recipients (:obj:`InputBusinessBotRecipients <pyroherd.raw.base.InputBusinessBotRecipients>`):
            N/A

        deleted (``bool``, *optional*):
            N/A

        rights (:obj:`BusinessBotRights <pyroherd.raw.base.BusinessBotRights>`, *optional*):
            N/A

    Returns:
        :obj:`Updates <pyroherd.raw.base.Updates>`
    """

    __slots__: List[str] = ["bot", "recipients", "deleted", "rights"]

    ID = 0x66a08c7e
    QUALNAME = "functions.account.UpdateConnectedBot"

    def __init__(self, *, bot: "raw.base.InputUser", recipients: "raw.base.InputBusinessBotRecipients", deleted: Optional[bool] = None, rights: "raw.base.BusinessBotRights" = None) -> None:
        self.bot = bot  # InputUser
        self.recipients = recipients  # InputBusinessBotRecipients
        self.deleted = deleted  # flags.1?true
        self.rights = rights  # flags.0?BusinessBotRights

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateConnectedBot":
        
        flags = Int.read(b)
        
        deleted = True if flags & (1 << 1) else False
        rights = TLObject.read(b) if flags & (1 << 0) else None
        
        bot = TLObject.read(b)
        
        recipients = TLObject.read(b)
        
        return UpdateConnectedBot(bot=bot, recipients=recipients, deleted=deleted, rights=rights)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.deleted else 0
        flags |= (1 << 0) if self.rights is not None else 0
        b.write(Int(flags))
        
        if self.rights is not None:
            b.write(self.rights.write())
        
        b.write(self.bot.write())
        
        b.write(self.recipients.write())
        
        return b.getvalue()
