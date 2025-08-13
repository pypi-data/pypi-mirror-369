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


class ToggleNoPaidMessagesException(TLObject):  # type: ignore
    """Allow a user to send us messages without paying if paid messages  are enabled.




    Details:
        - Layer: ``211``
        - ID: ``FE2EDA76``

    Parameters:
        user_id (:obj:`InputUser <pyrogram.raw.base.InputUser>`):
            The user to exempt or unexempt.

        refund_charged (``bool``, *optional*):
            If set and require_payment is not set, refunds the amounts the user has already paid us to send us messages (directly or via a monoforum).

        require_payment (``bool``, *optional*):
            If set, requires the user to pay in order to send us messages (can only be used by monoforums, not users, i.e. parent_peer must be set if this flag is set; users must instead use the inputPrivacyKeyNoPaidMessages                                                                privacy setting to remove a previously added exemption). If not set, allows the user to send us messages without paying (can be used by both monoforums and users).

        parent_peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`, *optional*):
            If set, applies the setting within the monoforum aka direct messages » (pass the ID of the monoforum, not the ID of the associated channel).

    Returns:
        ``bool``
    """

    __slots__: list[str] = ["user_id", "refund_charged", "require_payment", "parent_peer"]

    ID = 0xfe2eda76
    QUALNAME = "functions.account.ToggleNoPaidMessagesException"

    def __init__(self, *, user_id: "raw.base.InputUser", refund_charged: Optional[bool] = None, require_payment: Optional[bool] = None, parent_peer: "raw.base.InputPeer" = None) -> None:
        self.user_id = user_id  # InputUser
        self.refund_charged = refund_charged  # flags.0?true
        self.require_payment = require_payment  # flags.2?true
        self.parent_peer = parent_peer  # flags.1?InputPeer

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ToggleNoPaidMessagesException":
        
        flags = Int.read(b)
        
        refund_charged = True if flags & (1 << 0) else False
        require_payment = True if flags & (1 << 2) else False
        parent_peer = TLObject.read(b) if flags & (1 << 1) else None
        
        user_id = TLObject.read(b)
        
        return ToggleNoPaidMessagesException(user_id=user_id, refund_charged=refund_charged, require_payment=require_payment, parent_peer=parent_peer)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.refund_charged else 0
        flags |= (1 << 2) if self.require_payment else 0
        flags |= (1 << 1) if self.parent_peer is not None else 0
        b.write(Int(flags))
        
        if self.parent_peer is not None:
            b.write(self.parent_peer.write())
        
        b.write(self.user_id.write())
        
        return b.getvalue()
