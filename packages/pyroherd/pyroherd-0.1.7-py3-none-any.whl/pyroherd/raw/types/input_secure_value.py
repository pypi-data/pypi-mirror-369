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


class InputSecureValue(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.InputSecureValue`.

    Details:
        - Layer: ``201``
        - ID: ``DB21D0A7``

    Parameters:
        type (:obj:`SecureValueType <pyroherd.raw.base.SecureValueType>`):
            N/A

        data (:obj:`SecureData <pyroherd.raw.base.SecureData>`, *optional*):
            N/A

        front_side (:obj:`InputSecureFile <pyroherd.raw.base.InputSecureFile>`, *optional*):
            N/A

        reverse_side (:obj:`InputSecureFile <pyroherd.raw.base.InputSecureFile>`, *optional*):
            N/A

        selfie (:obj:`InputSecureFile <pyroherd.raw.base.InputSecureFile>`, *optional*):
            N/A

        translation (List of :obj:`InputSecureFile <pyroherd.raw.base.InputSecureFile>`, *optional*):
            N/A

        files (List of :obj:`InputSecureFile <pyroherd.raw.base.InputSecureFile>`, *optional*):
            N/A

        plain_data (:obj:`SecurePlainData <pyroherd.raw.base.SecurePlainData>`, *optional*):
            N/A

    """

    __slots__: List[str] = ["type", "data", "front_side", "reverse_side", "selfie", "translation", "files", "plain_data"]

    ID = 0xdb21d0a7
    QUALNAME = "types.InputSecureValue"

    def __init__(self, *, type: "raw.base.SecureValueType", data: "raw.base.SecureData" = None, front_side: "raw.base.InputSecureFile" = None, reverse_side: "raw.base.InputSecureFile" = None, selfie: "raw.base.InputSecureFile" = None, translation: Optional[List["raw.base.InputSecureFile"]] = None, files: Optional[List["raw.base.InputSecureFile"]] = None, plain_data: "raw.base.SecurePlainData" = None) -> None:
        self.type = type  # SecureValueType
        self.data = data  # flags.0?SecureData
        self.front_side = front_side  # flags.1?InputSecureFile
        self.reverse_side = reverse_side  # flags.2?InputSecureFile
        self.selfie = selfie  # flags.3?InputSecureFile
        self.translation = translation  # flags.6?Vector<InputSecureFile>
        self.files = files  # flags.4?Vector<InputSecureFile>
        self.plain_data = plain_data  # flags.5?SecurePlainData

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputSecureValue":
        
        flags = Int.read(b)
        
        type = TLObject.read(b)
        
        data = TLObject.read(b) if flags & (1 << 0) else None
        
        front_side = TLObject.read(b) if flags & (1 << 1) else None
        
        reverse_side = TLObject.read(b) if flags & (1 << 2) else None
        
        selfie = TLObject.read(b) if flags & (1 << 3) else None
        
        translation = TLObject.read(b) if flags & (1 << 6) else []
        
        files = TLObject.read(b) if flags & (1 << 4) else []
        
        plain_data = TLObject.read(b) if flags & (1 << 5) else None
        
        return InputSecureValue(type=type, data=data, front_side=front_side, reverse_side=reverse_side, selfie=selfie, translation=translation, files=files, plain_data=plain_data)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.data is not None else 0
        flags |= (1 << 1) if self.front_side is not None else 0
        flags |= (1 << 2) if self.reverse_side is not None else 0
        flags |= (1 << 3) if self.selfie is not None else 0
        flags |= (1 << 6) if self.translation else 0
        flags |= (1 << 4) if self.files else 0
        flags |= (1 << 5) if self.plain_data is not None else 0
        b.write(Int(flags))
        
        b.write(self.type.write())
        
        if self.data is not None:
            b.write(self.data.write())
        
        if self.front_side is not None:
            b.write(self.front_side.write())
        
        if self.reverse_side is not None:
            b.write(self.reverse_side.write())
        
        if self.selfie is not None:
            b.write(self.selfie.write())
        
        if self.translation is not None:
            b.write(Vector(self.translation))
        
        if self.files is not None:
            b.write(Vector(self.files))
        
        if self.plain_data is not None:
            b.write(self.plain_data.write())
        
        return b.getvalue()
