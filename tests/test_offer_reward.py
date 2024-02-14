from dexie_rewards.types.offer_reward import OfferReward


class TestOfferReward:
    def test_inactive_from_json_dict(self) -> None:
        json_dict = {
            "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
            "status": 4,
            "date_found": "2023-05-08T10:24:42.258Z",
            "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
            "rewards": [
                {
                    "amount": 31.326,
                    "code": "DBX",
                    "id": "db1a9020d48d9d4ad22631b66ab4b9ebd3637ef7758ad38881348c5d24c38f20",
                    "name": "dexie bucks",
                }
            ],
        }

        offer_reward = OfferReward.from_json_dict(json_dict)
        assert not offer_reward.is_active

    def test_active_from_json_dict(self) -> None:
        json_dict = {
            "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
            "status": 0,
            "date_found": "2023-05-08T10:24:42.258Z",
            "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
            "rewards": [
                {
                    "amount": 31.326,
                    "code": "DBX",
                    "id": "db1a9020d48d9d4ad22631b66ab4b9ebd3637ef7758ad38881348c5d24c38f20",
                    "name": "dexie bucks",
                }
            ],
        }

        offer_reward = OfferReward.from_json_dict(json_dict)
        assert offer_reward.is_active

    def test_float_from_json_dict(self) -> None:
        json_dict = {
            "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
            "status": 0,
            "date_found": "2023-05-08T10:24:42.258Z",
            "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
            "rewards": [
                {
                    "amount": 31.326,
                    "code": "DBX",
                    "id": "db1a9020d48d9d4ad22631b66ab4b9ebd3637ef7758ad38881348c5d24c38f20",
                    "name": "dexie bucks",
                },
                {
                    "amount": 20,
                    "code": "HOA",
                    "id": "e816ee18ce2337c4128449bc539fbbe2ecfdd2098c4e7cab4667e223c3bdc23d",
                    "name": "HOA COIN",
                },
            ],
        }

        offer_reward = OfferReward.from_json_dict(json_dict)
        dbx_reward = [r for r in offer_reward.rewards if r.code == "DBX"][0].amount
        assert dbx_reward == 31.326
