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

from typing import Union, List

import pyroherd
from pyroherd import raw


class ViewStories:
    async def view_stories(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
        story_id: Union[int, List[int]],
    ) -> bool:
        """Increment story views.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            story_id (``int`` | List of ``int``):
                Identifier or list of story identifiers of the target story.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Increment story views
                await app.view_stories(chat_id, 1)
        """
        ids = [story_id] if not isinstance(story_id, list) else story_id

        r = await self.invoke(
            raw.functions.stories.IncrementStoryViews(
                peer=await self.resolve_peer(chat_id),
                id=ids
            )
        )

        return r
