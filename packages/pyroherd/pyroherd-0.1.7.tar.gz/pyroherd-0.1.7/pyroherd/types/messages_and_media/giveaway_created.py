#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyroherd.
#
#  Pyroherd is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyroherd is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

import pyroherd

from pyroherd import raw
from ..object import Object



class GiveawayCreated(Object):
    """This object represents a service message about the creation of a scheduled giveaway.

    Parameters:
        prize_star_count (``int``, *optional*):
            The number of Telegram Stars to be split between giveaway winners.
            For Telegram Star giveaways only.
    """

    def __init__(
        self,
        *,
        client: "pyroherd.Client" = None,
        prize_star_count: Optional[int] = None
    ):
        super().__init__(client)

        self.prize_star_count = prize_star_count


    @staticmethod
    def _parse(
        client,
        giveaway_launch: "raw.types.MessageActionGiveawayLaunch"
    ) -> "GiveawayCreated":
        if isinstance(giveaway_launch, raw.types.MessageActionGiveawayLaunch):
            return GiveawayCreated(
                client=client,
                prize_star_count=getattr(giveaway_launch, "stars", None)
            )
