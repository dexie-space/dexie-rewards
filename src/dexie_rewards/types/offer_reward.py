from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from chia.types.blockchain_format.sized_bytes import bytes32

from dexie_rewards.types.utils import to_datetime


@dataclass
class Reward:
    amount: float
    code: str
    id: str
    name: str


@dataclass
class OfferReward:
    offer_id: str
    is_active: bool
    date_found: datetime
    maker_puzzle_hash: bytes32
    rewards: List[Reward]

    @classmethod
    def from_json_dict(cls, json_dict: Dict[str, Any]) -> "OfferReward":
        rewards = []
        if "rewards" in json_dict and json_dict["rewards"] is not None:
            for reward in json_dict["rewards"]:
                rewards.append(
                    Reward(
                        amount=round(
                            float(
                                reward["amount"],
                            ),
                            3,
                        ),
                        code=reward["code"],
                        id=reward["id"],
                        name=reward["name"],
                    )
                )
        return cls(
            offer_id=json_dict["id"],
            is_active=True if json_dict["status"] == 0 else False,
            date_found=to_datetime(json_dict["date_found"]),
            maker_puzzle_hash=bytes32.from_hexstr(json_dict["maker_puzzle_hash"]),
            rewards=rewards,
        )

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "id": self.offer_id,
            "is_active": self.is_active,
            "date_found": self.date_found.isoformat(),
            "maker_puzzle_hash": self.maker_puzzle_hash.hex(),
            "rewards": self.rewards,
        }
