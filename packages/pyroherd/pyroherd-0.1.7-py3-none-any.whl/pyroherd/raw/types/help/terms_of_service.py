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


class TermsOfService(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.help.TermsOfService`.

    Details:
        - Layer: ``201``
        - ID: ``780A0310``

    Parameters:
        id (:obj:`DataJSON <pyroherd.raw.base.DataJSON>`):
            N/A

        text (``str``):
            N/A

        entities (List of :obj:`MessageEntity <pyroherd.raw.base.MessageEntity>`):
            N/A

        popup (``bool``, *optional*):
            N/A

        min_age_confirm (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["id", "text", "entities", "popup", "min_age_confirm"]

    ID = 0x780a0310
    QUALNAME = "types.help.TermsOfService"

    def __init__(self, *, id: "raw.base.DataJSON", text: str, entities: List["raw.base.MessageEntity"], popup: Optional[bool] = None, min_age_confirm: Optional[int] = None) -> None:
        self.id = id  # DataJSON
        self.text = text  # string
        self.entities = entities  # Vector<MessageEntity>
        self.popup = popup  # flags.0?true
        self.min_age_confirm = min_age_confirm  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "TermsOfService":
        
        flags = Int.read(b)
        
        popup = True if flags & (1 << 0) else False
        id = TLObject.read(b)
        
        text = String.read(b)
        
        entities = TLObject.read(b)
        
        min_age_confirm = Int.read(b) if flags & (1 << 1) else None
        return TermsOfService(id=id, text=text, entities=entities, popup=popup, min_age_confirm=min_age_confirm)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.popup else 0
        flags |= (1 << 1) if self.min_age_confirm is not None else 0
        b.write(Int(flags))
        
        b.write(self.id.write())
        
        b.write(String(self.text))
        
        b.write(Vector(self.entities))
        
        if self.min_age_confirm is not None:
            b.write(Int(self.min_age_confirm))
        
        return b.getvalue()
