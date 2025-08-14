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


class StarsRevenueStats(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.payments.StarsRevenueStats`.

    Details:
        - Layer: ``201``
        - ID: ``C92BB73B``

    Parameters:
        revenue_graph (:obj:`StatsGraph <pyroherd.raw.base.StatsGraph>`):
            N/A

        status (:obj:`StarsRevenueStatus <pyroherd.raw.base.StarsRevenueStatus>`):
            N/A

        usd_rate (``float`` ``64-bit``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            payments.GetStarsRevenueStats
    """

    __slots__: List[str] = ["revenue_graph", "status", "usd_rate"]

    ID = 0xc92bb73b
    QUALNAME = "types.payments.StarsRevenueStats"

    def __init__(self, *, revenue_graph: "raw.base.StatsGraph", status: "raw.base.StarsRevenueStatus", usd_rate: float) -> None:
        self.revenue_graph = revenue_graph  # StatsGraph
        self.status = status  # StarsRevenueStatus
        self.usd_rate = usd_rate  # double

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarsRevenueStats":
        # No flags
        
        revenue_graph = TLObject.read(b)
        
        status = TLObject.read(b)
        
        usd_rate = Double.read(b)
        
        return StarsRevenueStats(revenue_graph=revenue_graph, status=status, usd_rate=usd_rate)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.revenue_graph.write())
        
        b.write(self.status.write())
        
        b.write(Double(self.usd_rate))
        
        return b.getvalue()
