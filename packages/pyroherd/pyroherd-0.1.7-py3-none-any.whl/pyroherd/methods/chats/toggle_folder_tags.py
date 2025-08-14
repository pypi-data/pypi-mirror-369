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

import pyroherd
from pyroherd import raw


class ToggleFolderTags:
    async def toggle_folder_tags(
        self: "pyroherd.Client",
        enabled: bool
    ) -> bool:
        """Toggle folder tags.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            enabled (``bool``):
                The new status. Pass True to enable folder tags.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.toggle_folder_tags(True)
        """
        r = await self.invoke(
            raw.functions.messages.ToggleDialogFilterTags(
                enabled=enabled
            )
        )

        return r
