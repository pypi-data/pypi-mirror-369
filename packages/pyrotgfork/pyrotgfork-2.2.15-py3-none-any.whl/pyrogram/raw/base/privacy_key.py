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

PrivacyKey = Union[raw.types.PrivacyKeyAbout, raw.types.PrivacyKeyAddedByPhone, raw.types.PrivacyKeyBirthday, raw.types.PrivacyKeyChatInvite, raw.types.PrivacyKeyForwards, raw.types.PrivacyKeyNoPaidMessages, raw.types.PrivacyKeyPhoneCall, raw.types.PrivacyKeyPhoneNumber, raw.types.PrivacyKeyPhoneP2P, raw.types.PrivacyKeyProfilePhoto, raw.types.PrivacyKeyStarGiftsAutoSave, raw.types.PrivacyKeyStatusTimestamp, raw.types.PrivacyKeyVoiceMessages]
PrivacyKey.__doc__ = """
    Privacy keys together with privacy rules  indicate what can or can't someone do and are specified by a PrivacyKey constructor, and its input counterpart InputPrivacyKey.
See the privacy documentation  for more info.

Telegram allows users to specify granular privacy settings, choosing which users can or can't interact with them in certain ways.
Privacy keys together with privacy rules  indicate what can or can't someone do and are specified by a PrivacyKey constructor, and its input counterpart InputPrivacyKey.
See the privacy documentation  for more info.


    Constructors:
        This base type has 13 constructors available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            PrivacyKeyAbout
            PrivacyKeyAddedByPhone
            PrivacyKeyBirthday
            PrivacyKeyChatInvite
            PrivacyKeyForwards
            PrivacyKeyNoPaidMessages
            PrivacyKeyPhoneCall
            PrivacyKeyPhoneNumber
            PrivacyKeyPhoneP2P
            PrivacyKeyProfilePhoto
            PrivacyKeyStarGiftsAutoSave
            PrivacyKeyStatusTimestamp
            PrivacyKeyVoiceMessages
"""
