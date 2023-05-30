import pytest

from dexie_rewards.types.offer_reward import OfferReward


class TestOfferReward:
    def test_inactive_from_json_dict(self) -> None:
        json_dict = {
            "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
            "status": 4,
            "date_found": "2023-05-08T10:24:42.258Z",
            "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
            "claimable_rewards": 0.8052,
        }

        offer_reward = OfferReward.from_json_dict(json_dict)
        assert offer_reward.is_active == False

    def test_active_from_json_dict(self) -> None:
        json_dict = {
            "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
            "status": 0,
            "date_found": "2023-05-08T10:24:42.258Z",
            "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
            "claimable_rewards": 0.8052,
        }

        offer_reward = OfferReward.from_json_dict(json_dict)
        assert offer_reward.is_active == True

    def test_float_from_json_dict(self) -> None:
        json_dict = {
            "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
            "status": 0,
            "date_found": "2023-05-08T10:24:42.258Z",
            "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
            "claimable_rewards": 0.8052,
        }

        offer_reward = OfferReward.from_json_dict(json_dict)
        assert offer_reward.claimable_rewards == 0.805
