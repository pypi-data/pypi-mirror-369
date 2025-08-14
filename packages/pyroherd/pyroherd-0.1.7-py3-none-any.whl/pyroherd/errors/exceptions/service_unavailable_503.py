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


class ServiceUnavailable(RPCError):
    """Service Unavailable"""
    CODE = 503
    """``int``: RPC Error Code"""
    NAME = __doc__


class ApiCallError(ServiceUnavailable):
    """Telegram is having internal problems. Please try again later."""
    ID = "ApiCallError"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class Timedout(ServiceUnavailable):
    """Telegram is having internal problems. Please try again later."""
    ID = "Timedout"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class Timeout(ServiceUnavailable):
    """Telegram is having internal problems. Please try again later."""
    ID = "Timeout"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


