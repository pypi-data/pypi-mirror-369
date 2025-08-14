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


class BroadcastRevenueStats(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.stats.BroadcastRevenueStats`.

    Details:
        - Layer: ``201``
        - ID: ``5407E297``

    Parameters:
        top_hours_graph (:obj:`StatsGraph <pyroherd.raw.base.StatsGraph>`):
            N/A

        revenue_graph (:obj:`StatsGraph <pyroherd.raw.base.StatsGraph>`):
            N/A

        balances (:obj:`BroadcastRevenueBalances <pyroherd.raw.base.BroadcastRevenueBalances>`):
            N/A

        usd_rate (``float`` ``64-bit``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            stats.GetBroadcastRevenueStats
    """

    __slots__: List[str] = ["top_hours_graph", "revenue_graph", "balances", "usd_rate"]

    ID = 0x5407e297
    QUALNAME = "types.stats.BroadcastRevenueStats"

    def __init__(self, *, top_hours_graph: "raw.base.StatsGraph", revenue_graph: "raw.base.StatsGraph", balances: "raw.base.BroadcastRevenueBalances", usd_rate: float) -> None:
        self.top_hours_graph = top_hours_graph  # StatsGraph
        self.revenue_graph = revenue_graph  # StatsGraph
        self.balances = balances  # BroadcastRevenueBalances
        self.usd_rate = usd_rate  # double

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BroadcastRevenueStats":
        # No flags
        
        top_hours_graph = TLObject.read(b)
        
        revenue_graph = TLObject.read(b)
        
        balances = TLObject.read(b)
        
        usd_rate = Double.read(b)
        
        return BroadcastRevenueStats(top_hours_graph=top_hours_graph, revenue_graph=revenue_graph, balances=balances, usd_rate=usd_rate)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.top_hours_graph.write())
        
        b.write(self.revenue_graph.write())
        
        b.write(self.balances.write())
        
        b.write(Double(self.usd_rate))
        
        return b.getvalue()
