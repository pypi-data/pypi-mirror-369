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

from ..object import Object


class InputPrivacyRule(Object):
    """Content of a privacy rule.

    It should be one of:

    - :obj:`~pyroherd.types.InputPrivacyRuleAllowAll`
    - :obj:`~pyroherd.types.InputPrivacyRuleAllowContacts`
    - :obj:`~pyroherd.types.InputPrivacyRuleAllowPremium`
    - :obj:`~pyroherd.types.InputPrivacyRuleAllowUsers`
    - :obj:`~pyroherd.types.InputPrivacyRuleAllowChats`
    - :obj:`~pyroherd.types.InputPrivacyRuleDisallowAll`
    - :obj:`~pyroherd.types.InputPrivacyRuleDisallowContacts`
    - :obj:`~pyroherd.types.InputPrivacyRuleDisallowUsers`
    - :obj:`~pyroherd.types.InputPrivacyRuleDisallowChats`
    """

    def __init__(self):
        super().__init__()

    async def write(self, client: "pyroherd.Client"):
        raise NotImplementedError
