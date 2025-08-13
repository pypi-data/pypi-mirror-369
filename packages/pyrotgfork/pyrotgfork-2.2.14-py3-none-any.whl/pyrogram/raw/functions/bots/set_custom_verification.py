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

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class SetCustomVerification(TLObject):  # type: ignore
    """Verify a user or chat on behalf of an organization ».


    Details:
        - Layer: ``211``
        - ID: ``8B89DFBD``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            The peer to verify

        enabled (``bool``, *optional*):
            If set, adds the verification; otherwise removes verification.

        bot (:obj:`InputUser <pyrogram.raw.base.InputUser>`, *optional*):
            Must not be set if invoked by a bot, must be set to the ID of an owned bot if invoked by a user.

        custom_description (``str``, *optional*):
            Custom description for the verification, the UTF-8 length limit for this field is contained in bot_verification_description_length_limit ». If not set, Was verified by organization "organization_name" will be used as description.

    Returns:
        ``bool``
    """

    __slots__: list[str] = ["peer", "enabled", "bot", "custom_description"]

    ID = 0x8b89dfbd
    QUALNAME = "functions.bots.SetCustomVerification"

    def __init__(self, *, peer: "raw.base.InputPeer", enabled: Optional[bool] = None, bot: "raw.base.InputUser" = None, custom_description: Optional[str] = None) -> None:
        self.peer = peer  # InputPeer
        self.enabled = enabled  # flags.1?true
        self.bot = bot  # flags.0?InputUser
        self.custom_description = custom_description  # flags.2?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetCustomVerification":
        
        flags = Int.read(b)
        
        enabled = True if flags & (1 << 1) else False
        bot = TLObject.read(b) if flags & (1 << 0) else None
        
        peer = TLObject.read(b)
        
        custom_description = String.read(b) if flags & (1 << 2) else None
        return SetCustomVerification(peer=peer, enabled=enabled, bot=bot, custom_description=custom_description)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.enabled else 0
        flags |= (1 << 0) if self.bot is not None else 0
        flags |= (1 << 2) if self.custom_description is not None else 0
        b.write(Int(flags))
        
        if self.bot is not None:
            b.write(self.bot.write())
        
        b.write(self.peer.write())
        
        if self.custom_description is not None:
            b.write(String(self.custom_description))
        
        return b.getvalue()
