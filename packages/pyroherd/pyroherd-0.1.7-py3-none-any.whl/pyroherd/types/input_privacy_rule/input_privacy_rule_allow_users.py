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

import asyncio
from typing import Union, Iterable

import pyroherd
from pyroherd import raw
from .input_privacy_rule import InputPrivacyRule


class InputPrivacyRuleAllowUsers(InputPrivacyRule):
    """Allow only participants of certain users.

    Parameters:
        chat_ids (``int`` | ``str`` | Iterable of ``int`` or ``str``, *optional*):
            Unique identifier (int) or username (str) of the target chat.
    """

    def __init__(
        self,
        chat_ids: Union[int, str, Iterable[Union[int, str]]],
    ):
        super().__init__()

        self.chat_ids = chat_ids

    async def write(self, client: "pyroherd.Client"):
        users = list(self.chat_ids) if not isinstance(self.chat_ids, (int, str)) else [self.chat_ids]
        users = await asyncio.gather(*[client.resolve_peer(i) for i in users])

        return raw.types.InputPrivacyValueAllowUsers(users=users)
