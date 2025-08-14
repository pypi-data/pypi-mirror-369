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

from typing import Union

import pyroherd
from pyroherd import raw
from pyroherd import types


class GetBoosts:
    async def get_boosts(
        self: "pyroherd.Client",
    ) -> bool:
        """Get your boosts list

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyroherd.types.MyBoost`: On success.

        Example:
            .. code-block:: python

                # get boosts list
                app.get_boosts()
        """
        r = await self.invoke(
            raw.functions.premium.GetMyBoosts()
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        return types.List(
            types.MyBoost._parse(
                self,
                boost,
                users,
                chats,
            ) for boost in r.my_boosts
        )
