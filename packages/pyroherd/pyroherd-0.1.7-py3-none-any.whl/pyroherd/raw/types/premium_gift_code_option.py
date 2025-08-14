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


class PremiumGiftCodeOption(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.PremiumGiftCodeOption`.

    Details:
        - Layer: ``201``
        - ID: ``257E962B``

    Parameters:
        users (``int`` ``32-bit``):
            N/A

        months (``int`` ``32-bit``):
            N/A

        currency (``str``):
            N/A

        amount (``int`` ``64-bit``):
            N/A

        store_product (``str``, *optional*):
            N/A

        store_quantity (``int`` ``32-bit``, *optional*):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            payments.GetPremiumGiftCodeOptions
    """

    __slots__: List[str] = ["users", "months", "currency", "amount", "store_product", "store_quantity"]

    ID = 0x257e962b
    QUALNAME = "types.PremiumGiftCodeOption"

    def __init__(self, *, users: int, months: int, currency: str, amount: int, store_product: Optional[str] = None, store_quantity: Optional[int] = None) -> None:
        self.users = users  # int
        self.months = months  # int
        self.currency = currency  # string
        self.amount = amount  # long
        self.store_product = store_product  # flags.0?string
        self.store_quantity = store_quantity  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PremiumGiftCodeOption":
        
        flags = Int.read(b)
        
        users = Int.read(b)
        
        months = Int.read(b)
        
        store_product = String.read(b) if flags & (1 << 0) else None
        store_quantity = Int.read(b) if flags & (1 << 1) else None
        currency = String.read(b)
        
        amount = Long.read(b)
        
        return PremiumGiftCodeOption(users=users, months=months, currency=currency, amount=amount, store_product=store_product, store_quantity=store_quantity)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.store_product is not None else 0
        flags |= (1 << 1) if self.store_quantity is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.users))
        
        b.write(Int(self.months))
        
        if self.store_product is not None:
            b.write(String(self.store_product))
        
        if self.store_quantity is not None:
            b.write(Int(self.store_quantity))
        
        b.write(String(self.currency))
        
        b.write(Long(self.amount))
        
        return b.getvalue()
