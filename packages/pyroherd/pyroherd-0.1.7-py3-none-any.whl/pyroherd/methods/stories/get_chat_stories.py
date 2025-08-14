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

from typing import AsyncGenerator, Union

import pyroherd
from pyroherd import raw
from pyroherd import types


class GetChatStories:
    async def get_chat_stories(
        self: "pyroherd.Client",
        chat_id: Union[int, str]
    ) -> AsyncGenerator["types.Story", None]:
        """Get all non expired stories from a chat by using chat identifier.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.
                For your personal story you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~pyroherd.types.Story` objects is returned.

        Example:
            .. code-block:: python

                # Get all non expired stories from spesific chat
                async for story in app.get_chat_stories(chat_id):
                    print(story)

        Raises:
            ValueError: In case of invalid arguments.
        """
        peer = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.stories.GetPeerStories(
                peer=peer
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for story in r.stories.stories:
            yield await types.Story._parse(
                self,
                story,
                users,
                chats,
                r.stories.peer
            )
