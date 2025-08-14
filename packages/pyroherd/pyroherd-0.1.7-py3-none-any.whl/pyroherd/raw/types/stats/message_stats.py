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


class MessageStats(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyroherd.raw.base.stats.MessageStats`.

    Details:
        - Layer: ``201``
        - ID: ``7FE91C14``

    Parameters:
        views_graph (:obj:`StatsGraph <pyroherd.raw.base.StatsGraph>`):
            N/A

        reactions_by_emotion_graph (:obj:`StatsGraph <pyroherd.raw.base.StatsGraph>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyroherd.raw.functions

        .. autosummary::
            :nosignatures:

            stats.GetMessageStats
    """

    __slots__: List[str] = ["views_graph", "reactions_by_emotion_graph"]

    ID = 0x7fe91c14
    QUALNAME = "types.stats.MessageStats"

    def __init__(self, *, views_graph: "raw.base.StatsGraph", reactions_by_emotion_graph: "raw.base.StatsGraph") -> None:
        self.views_graph = views_graph  # StatsGraph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph  # StatsGraph

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageStats":
        # No flags
        
        views_graph = TLObject.read(b)
        
        reactions_by_emotion_graph = TLObject.read(b)
        
        return MessageStats(views_graph=views_graph, reactions_by_emotion_graph=reactions_by_emotion_graph)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.views_graph.write())
        
        b.write(self.reactions_by_emotion_graph.write())
        
        return b.getvalue()
