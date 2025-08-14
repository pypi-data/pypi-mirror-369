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

from typing import Union, Optional

import pyroherd
from pyroherd import raw


class SetPersonalChannel:
    async def set_personal_channel(
        self: "pyroherd.Client",
        chat_id: Optional[Union[int, str]] = None
    ) -> bool:
        """Set a personal channel in bio.

        .. include:: /_includes/usable-by/users.rst

        To get all available channels you can use
        :meth:`~pyroherd.Client.get_personal_channels`.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user or None to remove it.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Set your personal channel
                await app.set_personal_channel(chat_id)

                # Remove personal channel from your profile
                await app.set_personal_channel()
        """
        if chat_id is None:
            peer = raw.types.InputChannelEmpty()
        else:
            peer = await self.resolve_peer(chat_id)

            if not isinstance(peer, raw.types.InputPeerChannel):
                return False

        return bool(
            await self.invoke(
                raw.functions.account.UpdatePersonalChannel(
                    channel=peer
                )
            )
        )
