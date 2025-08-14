# <<<<<<< HEAD
# =======
# <<<<<<< HEAD
# >>>>>>> c723d0e (update)
# Pyroherd - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-present OnTheHerd <https://github.com/OnTheHerd>
#
# This file is part of Pyroherd.
#
# Pyroherd is free software: you can redistribute it and/or modify
# <<<<<<< HEAD
# =======
# =======
# Pyroherd - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
# This file is part of Pyroherd.
#
# Pyroherd is free software: you can redistribute it and/or modify
# >>>>>>> 47ad949 (update)
# >>>>>>> c723d0e (update)
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# <<<<<<< HEAD
# Pyroherd is distributed in the hope that it will be useful,
# =======
# <<<<<<< HEAD
# Pyroherd is distributed in the hope that it will be useful,
# =======
# Pyroherd is distributed in the hope that it will be useful,
# >>>>>>> 47ad949 (update)
# >>>>>>> c723d0e (update)
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# <<<<<<< HEAD
# along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.
# =======
# <<<<<<< HEAD
# along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.
# =======
# along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.
# >>>>>>> 47ad949 (update)
# >>>>>>> c723d0e (update)

from ..rpc_error import RPCError


class SeeOther(RPCError):
    """See Other"""
    CODE = 303
    """``int``: RPC Error Code"""
    NAME = __doc__


class FileMigrate(SeeOther):
    """The file to be accessed is currently stored in DC{value}"""
    ID = "FILE_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NetworkMigrate(SeeOther):
    """The source IP address is associated with DC{value} (for registration)"""
    ID = "NETWORK_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneMigrate(SeeOther):
    """The phone number a user is trying to use for authorization is associated with DC{value}"""
    ID = "PHONE_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StatsMigrate(SeeOther):
    """The statistics of the group/channel are stored in DC{value}"""
    ID = "STATS_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserMigrate(SeeOther):
    """The user whose identity is being used to execute queries is associated with DC{value} (for registration)"""
    ID = "USER_MIGRATE_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


