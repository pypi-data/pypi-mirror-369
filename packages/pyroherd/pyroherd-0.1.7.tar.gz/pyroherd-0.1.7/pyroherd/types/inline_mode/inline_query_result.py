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

from uuid import uuid4

import pyroherd
from pyroherd import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~pyroherd.types.InlineQueryResultCachedAudio`
    - :obj:`~pyroherd.types.InlineQueryResultCachedDocument`
    - :obj:`~pyroherd.types.InlineQueryResultCachedAnimation`
    - :obj:`~pyroherd.types.InlineQueryResultCachedPhoto`
    - :obj:`~pyroherd.types.InlineQueryResultCachedSticker`
    - :obj:`~pyroherd.types.InlineQueryResultCachedVideo`
    - :obj:`~pyroherd.types.InlineQueryResultCachedVoice`
    - :obj:`~pyroherd.types.InlineQueryResultArticle`
    - :obj:`~pyroherd.types.InlineQueryResultAudio`
    - :obj:`~pyroherd.types.InlineQueryResultContact`
    - :obj:`~pyroherd.types.InlineQueryResultDocument`
    - :obj:`~pyroherd.types.InlineQueryResultAnimation`
    - :obj:`~pyroherd.types.InlineQueryResultLocation`
    - :obj:`~pyroherd.types.InlineQueryResultPhoto`
    - :obj:`~pyroherd.types.InlineQueryResultVenue`
    - :obj:`~pyroherd.types.InlineQueryResultVideo`
    - :obj:`~pyroherd.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "pyroherd.Client"):
        pass
