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


class SavedStarGift(TLObject):  # type: ignore
    """


    Constructor of :obj:`~pyrogram.raw.base.SavedStarGift`.

    Details:
        - Layer: ``211``
        - ID: ``1EA646DF``

    Parameters:
        date (``int`` ``32-bit``):
            

        gift (:obj:`StarGift <pyrogram.raw.base.StarGift>`):
            

        name_hidden (``bool``, *optional*):
            

        unsaved (``bool``, *optional*):
            

        refunded (``bool``, *optional*):
            

        can_upgrade (``bool``, *optional*):
            

        pinned_to_top (``bool``, *optional*):
            

        from_id (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            

        message (:obj:`TextWithEntities <pyrogram.raw.base.TextWithEntities>`, *optional*):
            

        msg_id (``int`` ``32-bit``, *optional*):
            

        saved_id (``int`` ``64-bit``, *optional*):
            

        convert_stars (``int`` ``64-bit``, *optional*):
            

        upgrade_stars (``int`` ``64-bit``, *optional*):
            

        can_export_at (``int`` ``32-bit``, *optional*):
            

        transfer_stars (``int`` ``64-bit``, *optional*):
            

        can_transfer_at (``int`` ``32-bit``, *optional*):
            

        can_resell_at (``int`` ``32-bit``, *optional*):
            

        collection_id (List of ``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: list[str] = ["date", "gift", "name_hidden", "unsaved", "refunded", "can_upgrade", "pinned_to_top", "from_id", "message", "msg_id", "saved_id", "convert_stars", "upgrade_stars", "can_export_at", "transfer_stars", "can_transfer_at", "can_resell_at", "collection_id"]

    ID = 0x1ea646df
    QUALNAME = "types.SavedStarGift"

    def __init__(self, *, date: int, gift: "raw.base.StarGift", name_hidden: Optional[bool] = None, unsaved: Optional[bool] = None, refunded: Optional[bool] = None, can_upgrade: Optional[bool] = None, pinned_to_top: Optional[bool] = None, from_id: "raw.base.Peer" = None, message: "raw.base.TextWithEntities" = None, msg_id: Optional[int] = None, saved_id: Optional[int] = None, convert_stars: Optional[int] = None, upgrade_stars: Optional[int] = None, can_export_at: Optional[int] = None, transfer_stars: Optional[int] = None, can_transfer_at: Optional[int] = None, can_resell_at: Optional[int] = None, collection_id: Optional[list[int]] = None) -> None:
        self.date = date  # int
        self.gift = gift  # StarGift
        self.name_hidden = name_hidden  # flags.0?true
        self.unsaved = unsaved  # flags.5?true
        self.refunded = refunded  # flags.9?true
        self.can_upgrade = can_upgrade  # flags.10?true
        self.pinned_to_top = pinned_to_top  # flags.12?true
        self.from_id = from_id  # flags.1?Peer
        self.message = message  # flags.2?TextWithEntities
        self.msg_id = msg_id  # flags.3?int
        self.saved_id = saved_id  # flags.11?long
        self.convert_stars = convert_stars  # flags.4?long
        self.upgrade_stars = upgrade_stars  # flags.6?long
        self.can_export_at = can_export_at  # flags.7?int
        self.transfer_stars = transfer_stars  # flags.8?long
        self.can_transfer_at = can_transfer_at  # flags.13?int
        self.can_resell_at = can_resell_at  # flags.14?int
        self.collection_id = collection_id  # flags.15?Vector<int>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SavedStarGift":
        
        flags = Int.read(b)
        
        name_hidden = True if flags & (1 << 0) else False
        unsaved = True if flags & (1 << 5) else False
        refunded = True if flags & (1 << 9) else False
        can_upgrade = True if flags & (1 << 10) else False
        pinned_to_top = True if flags & (1 << 12) else False
        from_id = TLObject.read(b) if flags & (1 << 1) else None
        
        date = Int.read(b)
        
        gift = TLObject.read(b)
        
        message = TLObject.read(b) if flags & (1 << 2) else None
        
        msg_id = Int.read(b) if flags & (1 << 3) else None
        saved_id = Long.read(b) if flags & (1 << 11) else None
        convert_stars = Long.read(b) if flags & (1 << 4) else None
        upgrade_stars = Long.read(b) if flags & (1 << 6) else None
        can_export_at = Int.read(b) if flags & (1 << 7) else None
        transfer_stars = Long.read(b) if flags & (1 << 8) else None
        can_transfer_at = Int.read(b) if flags & (1 << 13) else None
        can_resell_at = Int.read(b) if flags & (1 << 14) else None
        collection_id = TLObject.read(b, Int) if flags & (1 << 15) else []
        
        return SavedStarGift(date=date, gift=gift, name_hidden=name_hidden, unsaved=unsaved, refunded=refunded, can_upgrade=can_upgrade, pinned_to_top=pinned_to_top, from_id=from_id, message=message, msg_id=msg_id, saved_id=saved_id, convert_stars=convert_stars, upgrade_stars=upgrade_stars, can_export_at=can_export_at, transfer_stars=transfer_stars, can_transfer_at=can_transfer_at, can_resell_at=can_resell_at, collection_id=collection_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.name_hidden else 0
        flags |= (1 << 5) if self.unsaved else 0
        flags |= (1 << 9) if self.refunded else 0
        flags |= (1 << 10) if self.can_upgrade else 0
        flags |= (1 << 12) if self.pinned_to_top else 0
        flags |= (1 << 1) if self.from_id is not None else 0
        flags |= (1 << 2) if self.message is not None else 0
        flags |= (1 << 3) if self.msg_id is not None else 0
        flags |= (1 << 11) if self.saved_id is not None else 0
        flags |= (1 << 4) if self.convert_stars is not None else 0
        flags |= (1 << 6) if self.upgrade_stars is not None else 0
        flags |= (1 << 7) if self.can_export_at is not None else 0
        flags |= (1 << 8) if self.transfer_stars is not None else 0
        flags |= (1 << 13) if self.can_transfer_at is not None else 0
        flags |= (1 << 14) if self.can_resell_at is not None else 0
        flags |= (1 << 15) if self.collection_id else 0
        b.write(Int(flags))
        
        if self.from_id is not None:
            b.write(self.from_id.write())
        
        b.write(Int(self.date))
        
        b.write(self.gift.write())
        
        if self.message is not None:
            b.write(self.message.write())
        
        if self.msg_id is not None:
            b.write(Int(self.msg_id))
        
        if self.saved_id is not None:
            b.write(Long(self.saved_id))
        
        if self.convert_stars is not None:
            b.write(Long(self.convert_stars))
        
        if self.upgrade_stars is not None:
            b.write(Long(self.upgrade_stars))
        
        if self.can_export_at is not None:
            b.write(Int(self.can_export_at))
        
        if self.transfer_stars is not None:
            b.write(Long(self.transfer_stars))
        
        if self.can_transfer_at is not None:
            b.write(Int(self.can_transfer_at))
        
        if self.can_resell_at is not None:
            b.write(Int(self.can_resell_at))
        
        if self.collection_id is not None:
            b.write(Vector(self.collection_id, Int))
        
        return b.getvalue()
