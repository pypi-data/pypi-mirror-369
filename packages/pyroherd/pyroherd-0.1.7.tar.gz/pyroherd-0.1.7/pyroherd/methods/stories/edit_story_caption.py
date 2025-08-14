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

from typing import List, Union

import pyroherd
from pyroherd import enums, raw, types, utils

class EditStoryCaption:
    async def edit_story_caption(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
        story_id: int,
        caption: str,
        parse_mode: "enums.ParseMode" = None,
        caption_entities: List["types.MessageEntity"] = None,
    ) -> "types.Story":
        """Edit the caption of story.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            story_id (``int``):
                Story identifier in the chat specified in chat_id.

            caption (``str``):
                New caption of the story, 0-1024 characters.

            parse_mode (:obj:`~pyroherd.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyroherd.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        Returns:
            :obj:`~pyroherd.types.Story`: On success, the edited story is returned.

        Example:
            .. code-block:: python

                await app.edit_story(chat_id, story_id, "new media caption")
        """

        message, entities = (await utils.parse_text_entities(self, caption, parse_mode, caption_entities)).values()

        r = await self.invoke(
            raw.functions.stories.EditStory(
                peer=await self.resolve_peer(chat_id),
                id=story_id,
                caption=message,
                entities=entities,
            )
        )

        for i in r.updates:
            if isinstance(i, raw.types.UpdateStory):
                return await types.Story._parse(
                    self,
                    i.story,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    i.peer
                )
