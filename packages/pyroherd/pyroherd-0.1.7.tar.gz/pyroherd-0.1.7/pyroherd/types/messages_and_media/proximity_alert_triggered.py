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
from typing import Dict

import pyroherd
from pyroherd import raw, types, utils

from ..object import Object


class ProximityAlertTriggered(Object):
    """Information about a proximity alert.

    Parameters:
        traveler (:obj:`~pyroherd.types.User`):
            Chat that triggered the proximity alert.

        watcher (:obj:`~pyroherd.types.User`):
            Chat that subscribed for the proximity alert.

        distance (``str``):
            The distance between the users.
    """
    def __init__(
        self, *,
        traveler: "pyroherd.types.User",
        watcher: "pyroherd.types.User",
        distance: str
    ):
        super().__init__()

        self.traveler = traveler
        self.watcher = watcher
        self.distance = distance

    @staticmethod
    def _parse(
        client: "pyroherd.Client",
        action: "raw.types.MessageActionGeoProximityReached",
        users: Dict[int, "raw.base.User"],
        chats: Dict[int, "raw.base.Chat"]
    ) -> "ProximityAlertTriggered":
        from_id = utils.get_raw_peer_id(action.from_id)
        to_id = utils.get_raw_peer_id(action.to_id)

        return ProximityAlertTriggered(
            traveler=types.Chat._parse_chat(client, users.get(from_id) or chats.get(from_id)),
            watcher=types.Chat._parse_chat(client, users.get(to_id) or chats.get(to_id)),
            distance=action.distance
        )
