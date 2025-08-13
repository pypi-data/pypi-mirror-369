#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyrogram import raw

StarsTransactionPeer = Union[raw.types.StarsTransactionPeer, raw.types.StarsTransactionPeerAPI, raw.types.StarsTransactionPeerAds, raw.types.StarsTransactionPeerAppStore, raw.types.StarsTransactionPeerFragment, raw.types.StarsTransactionPeerPlayMarket, raw.types.StarsTransactionPeerPremiumBot, raw.types.StarsTransactionPeerUnsupported]
StarsTransactionPeer.__doc__ = """
    Source of an incoming Telegram Star transaction, or its recipient for outgoing Telegram Star transactions.

Telegram Stars are virtual items that allow users to purchase digital goods and services from bots and mini apps inside the Telegram ecosystem, send gifts to content creators on the Telegram platform, and more.


    Constructors:
        This base type has 8 constructors available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            StarsTransactionPeer
            StarsTransactionPeerAPI
            StarsTransactionPeerAds
            StarsTransactionPeerAppStore
            StarsTransactionPeerFragment
            StarsTransactionPeerPlayMarket
            StarsTransactionPeerPremiumBot
            StarsTransactionPeerUnsupported
"""
