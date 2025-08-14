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


class ReactionsNotifySettings(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.ReactionsNotifySettings`.

    Details:
        - Layer: ``201``
        - ID: ``56E34970``

    Parameters:
        sound (:obj:`NotificationSound <pyroherd.raw.base.NotificationSound>`):
            N/A

        show_previews (``bool``):
            N/A

        messages_notify_from (:obj:`ReactionNotificationsFrom <pyroherd.raw.base.ReactionNotificationsFrom>`, *optional*):
            N/A

        stories_notify_from (:obj:`ReactionNotificationsFrom <pyroherd.raw.base.ReactionNotificationsFrom>`, *optional*):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetReactionsNotifySettings
            account.SetReactionsNotifySettings
    """

    __slots__: List[str] = ["sound", "show_previews", "messages_notify_from", "stories_notify_from"]

    ID = 0x56e34970
    QUALNAME = "types.ReactionsNotifySettings"

    def __init__(self, *, sound: "raw.base.NotificationSound", show_previews: bool, messages_notify_from: "raw.base.ReactionNotificationsFrom" = None, stories_notify_from: "raw.base.ReactionNotificationsFrom" = None) -> None:
        self.sound = sound  # NotificationSound
        self.show_previews = show_previews  # Bool
        self.messages_notify_from = messages_notify_from  # flags.0?ReactionNotificationsFrom
        self.stories_notify_from = stories_notify_from  # flags.1?ReactionNotificationsFrom

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReactionsNotifySettings":
        
        flags = Int.read(b)
        
        messages_notify_from = TLObject.read(b) if flags & (1 << 0) else None
        
        stories_notify_from = TLObject.read(b) if flags & (1 << 1) else None
        
        sound = TLObject.read(b)
        
        show_previews = Bool.read(b)
        
        return ReactionsNotifySettings(sound=sound, show_previews=show_previews, messages_notify_from=messages_notify_from, stories_notify_from=stories_notify_from)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.messages_notify_from is not None else 0
        flags |= (1 << 1) if self.stories_notify_from is not None else 0
        b.write(Int(flags))
        
        if self.messages_notify_from is not None:
            b.write(self.messages_notify_from.write())
        
        if self.stories_notify_from is not None:
            b.write(self.stories_notify_from.write())
        
        b.write(self.sound.write())
        
        b.write(Bool(self.show_previews))
        
        return b.getvalue()
