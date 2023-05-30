from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from chia.types.blockchain_format.sized_bytes import bytes32

from .utils import to_datetime


@dataclass
class OfferReward:
    offer_id: str
    is_active: bool
    claimable_rewards: float
    date_found: datetime
    maker_puzzle_hash: bytes32

    @classmethod
    def from_json_dict(cls, json_dict: Dict[str, Any]) -> "OfferReward":
        return cls(
            offer_id=json_dict["id"],
            is_active=True if json_dict["status"] == 0 else False,
            claimable_rewards=round(float(json_dict["claimable_rewards"]), 3),
            date_found=to_datetime(json_dict["date_found"]),
            maker_puzzle_hash=bytes32.from_hexstr(json_dict["maker_puzzle_hash"]),
        )
