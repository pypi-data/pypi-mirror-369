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


class PremiumPromo(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.help.PremiumPromo`.

    Details:
        - Layer: ``201``
        - ID: ``5334759C``

    Parameters:
        status_text (``str``):
            N/A

        status_entities (List of :obj:`MessageEntity <pyroherd.raw.base.MessageEntity>`):
            N/A

        video_sections (List of ``str``):
            N/A

        videos (List of :obj:`Document <pyroherd.raw.base.Document>`):
            N/A

        period_options (List of :obj:`PremiumSubscriptionOption <pyroherd.raw.base.PremiumSubscriptionOption>`):
            N/A

        users (List of :obj:`User <pyroherd.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            help.GetPremiumPromo
    """

    __slots__: List[str] = ["status_text", "status_entities", "video_sections", "videos", "period_options", "users"]

    ID = 0x5334759c
    QUALNAME = "types.help.PremiumPromo"

    def __init__(self, *, status_text: str, status_entities: List["raw.base.MessageEntity"], video_sections: List[str], videos: List["raw.base.Document"], period_options: List["raw.base.PremiumSubscriptionOption"], users: List["raw.base.User"]) -> None:
        self.status_text = status_text  # string
        self.status_entities = status_entities  # Vector<MessageEntity>
        self.video_sections = video_sections  # Vector<string>
        self.videos = videos  # Vector<Document>
        self.period_options = period_options  # Vector<PremiumSubscriptionOption>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PremiumPromo":
        # No flags
        
        status_text = String.read(b)
        
        status_entities = TLObject.read(b)
        
        video_sections = TLObject.read(b, String)
        
        videos = TLObject.read(b)
        
        period_options = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return PremiumPromo(status_text=status_text, status_entities=status_entities, video_sections=video_sections, videos=videos, period_options=period_options, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.status_text))
        
        b.write(Vector(self.status_entities))
        
        b.write(Vector(self.video_sections, String))
        
        b.write(Vector(self.videos))
        
        b.write(Vector(self.period_options))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
