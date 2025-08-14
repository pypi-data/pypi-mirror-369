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


class PhoneCallProtocol(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.PhoneCallProtocol`.

    Details:
        - Layer: ``201``
        - ID: ``FC878FC8``

    Parameters:
        min_layer (``int`` ``32-bit``):
            N/A

        max_layer (``int`` ``32-bit``):
            N/A

        library_versions (List of ``str``):
            N/A

        udp_p2p (``bool``, *optional*):
            N/A

        udp_reflector (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["min_layer", "max_layer", "library_versions", "udp_p2p", "udp_reflector"]

    ID = 0xfc878fc8
    QUALNAME = "types.PhoneCallProtocol"

    def __init__(self, *, min_layer: int, max_layer: int, library_versions: List[str], udp_p2p: Optional[bool] = None, udp_reflector: Optional[bool] = None) -> None:
        self.min_layer = min_layer  # int
        self.max_layer = max_layer  # int
        self.library_versions = library_versions  # Vector<string>
        self.udp_p2p = udp_p2p  # flags.0?true
        self.udp_reflector = udp_reflector  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PhoneCallProtocol":
        
        flags = Int.read(b)
        
        udp_p2p = True if flags & (1 << 0) else False
        udp_reflector = True if flags & (1 << 1) else False
        min_layer = Int.read(b)
        
        max_layer = Int.read(b)
        
        library_versions = TLObject.read(b, String)
        
        return PhoneCallProtocol(min_layer=min_layer, max_layer=max_layer, library_versions=library_versions, udp_p2p=udp_p2p, udp_reflector=udp_reflector)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.udp_p2p else 0
        flags |= (1 << 1) if self.udp_reflector else 0
        b.write(Int(flags))
        
        b.write(Int(self.min_layer))
        
        b.write(Int(self.max_layer))
        
        b.write(Vector(self.library_versions, String))
        
        return b.getvalue()
