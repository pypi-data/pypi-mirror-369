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

from typing import Callable, Optional

import pyroherd


class OnDisconnect:
    def on_disconnect(self: Optional["OnDisconnect"] = None) -> Callable:
        """Decorator for handling disconnections.

        This does the same thing as :meth:`~pyroherd.Client.add_handler` using the
        :obj:`~pyroherd.handlers.DisconnectHandler`.
        """

        def decorator(func: Callable) -> Callable:
            if isinstance(self, pyroherd.Client):
                self.add_handler(pyroherd.handlers.DisconnectHandler(func))
            else:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append((pyroherd.handlers.DisconnectHandler(func), 0))

            return func

        return decorator
