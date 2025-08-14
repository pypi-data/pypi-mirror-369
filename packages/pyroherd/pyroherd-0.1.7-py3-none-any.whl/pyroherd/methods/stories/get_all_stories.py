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

from typing import AsyncGenerator, Optional

import pyroherd
from pyroherd import raw
from pyroherd import types


class GetAllStories:
    async def get_all_stories(
        self: "pyroherd.Client",
        next: Optional[bool] = None,
        hidden: Optional[bool] = None,
        state: Optional[str] = None,
    ) -> AsyncGenerator["types.Story", None]:
        """Get all active stories.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~pyroherd.types.Story` objects is returned.

        Example:
            .. code-block:: python

                # Get all active story
                async for story in app.get_all_stories():
                    print(story)

        Raises:
            ValueError: In case of invalid arguments.
        """

        r = await self.invoke(
            raw.functions.stories.GetAllStories(
                next=next,
                hidden=hidden,
                state=state
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for peer_story in r.peer_stories:
            for story in peer_story.stories:
                yield await types.Story._parse(
                    self,
                    story,
                    users,
                    chats,
                    peer_story.peer
                )
