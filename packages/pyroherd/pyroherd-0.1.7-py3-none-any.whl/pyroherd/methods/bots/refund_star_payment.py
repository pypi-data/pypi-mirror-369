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

from typing import Union

import pyroherd
from pyroherd import raw


class RefundStarPayment:
    async def refund_star_payment(
        self: "pyroherd.Client",
        user_id: Union[int, str],
        telegram_payment_charge_id: str
    ) -> bool:
        """Refunds a successful payment in `Telegram Stars <https://t.me/BotNews/90>`_.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user, whose payment will be refunded.

            telegram_payment_charge_id (``str``):
                Telegram payment identifier.

        Returns:
            ``bool``: True on success

        """

        r = await self.invoke(
            raw.functions.payments.RefundStarsCharge(
                user_id=await self.resolve_peer(user_id),
                charge_id=telegram_payment_charge_id
            )
        )
        
        return bool(r)
