#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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

from datetime import datetime

from pyroherd import enums, types

from .message_origin import MessageOrigin


class MessageOriginChannel(MessageOrigin):
    """The message was originally sent to a channel chat.

    Parameters:
        type (:obj:`~pyroherd.enums.MessageOriginType`):
            Type of the message origin.

        date (:py:obj:`~datetime.datetime`):
            Date the message was sent originally.

        chat (:obj:`~pyroherd.types.Chat`):
            Channel chat to which the message was originally sent.

        message_id (``int``):
            Unique message identifier inside the chat.

        author_signature (``str``, *optional*):
            Signature of the original post author.
    """
    def __init__(
        self,
        *,
        type: "enums.MessageOriginType" = enums.MessageOriginType.CHANNEL,
        date: datetime = None,
        chat: "types.Chat" = None,
        message_id: int = None,
        author_signature: str = None
    ):
        super().__init__(
            type=type,
            date=date
        )

        self.chat = chat
        self.message_id = message_id
        self.author_signature = author_signature
