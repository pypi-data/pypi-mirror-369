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

from pyroherd import raw, types

from ..object import Object


class PurchasedPaidMedia(Object):
    """This object represents information about purchased paid media.

    Parameters:
        from_user (:obj:`~pyroherd.types.User`):
            User who bought the paid media.

        payload (``str``):
            Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.
    """

    def __init__(
        self,
        from_user: "types.User",
        payload: str
    ):
        super().__init__()

        self.from_user = from_user
        self.payload = payload

    @staticmethod
    def _parse(client, purchased_media: "raw.types.UpdateBotPurchasedPaidMedia", users) -> "PurchasedPaidMedia":
        return PurchasedPaidMedia(
            from_user=types.User._parse(client, users.get(purchased_media.user_id)),
            payload=purchased_media.payload
        )
