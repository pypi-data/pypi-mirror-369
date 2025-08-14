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


class Flood(RPCError):
    """Flood"""
    CODE = 420
    """``int``: RPC Error Code"""
    NAME = __doc__


class TwoFaConfirmWait(Flood):
    """A wait of {value} seconds is required because this account is active and protected by a 2FA password"""
    ID = "2FA_CONFIRM_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodPremiumWait(Flood):
    """A wait of {value} seconds is required"""
    ID = "FLOOD_PREMIUM_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodTestPhoneWait(Flood):
    """A wait of {value} seconds is required in the test servers"""
    ID = "FLOOD_TEST_PHONE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodWait(Flood):
    """A wait of {value} seconds is required"""
    ID = "FLOOD_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumSubActiveUntil(Flood):
    """A wait of {value} seconds is required"""
    ID = "PREMIUM_SUB_ACTIVE_UNTIL_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlowmodeWait(Flood):
    """A wait of {value} seconds is required to send messages in this chat"""
    ID = "SLOWMODE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StorySendFlood(Flood):
    """A wait of {value} seconds is required to continue posting stories"""
    ID = "STORY_SEND_FLOOD_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutInitDelay(Flood):
    """You have to confirm the data export request using one of your mobile devices or wait {value} seconds"""
    ID = "TAKEOUT_INIT_DELAY_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


