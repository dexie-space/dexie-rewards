import aiohttp
import based58
import dataclasses
import hashlib
from typing import Any, Dict

from chia.wallet.trading.offer import Offer


def get_dexie_bs58_offer_hash(offer: Offer) -> str:
    m = hashlib.sha256()
    m.update(bytes(offer.to_bech32(), "utf-8"))
    offer_hash = m.hexdigest()
    offer_hash_bs58 = based58.b58encode(bytes.fromhex(offer_hash))
    return offer_hash_bs58.decode("utf-8")


@dataclasses.dataclass
class Api:
    base_url: str

    async def post_offer(self, offer: Offer) -> None:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/offers", json={"offer": offer.to_bech32()}
            ) as rep,
        ):
            if not rep.ok:
                raise RuntimeError(rep.reason)

    async def get_all_offers(self) -> list[Offer]:
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"{self.base_url}/offers") as rep,
        ):
            if not rep.ok:
                raise RuntimeError(rep.reason)
            return [Offer.from_bech32(offer) for offer in await rep.json()]

    # offer id or trade id
    async def get_offer(self, offer_id: str) -> Offer:
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"{self.base_url}/offers/{offer_id}") as rep,
        ):
            if not rep.ok:
                raise RuntimeError(rep.reason)
            return await rep.json()

    async def get_offers_with_claimable_rewards(
        self, offer_ids: list[str]
    ) -> Dict[str, Any]:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/rewards/check", json={"ids": offer_ids}
            ) as rep,
        ):
            if not rep.ok:
                raise RuntimeError(rep.reason)
            return await rep.json()

    # claim rewards
    async def claim_rewards(self, claims_payload: Dict[str, Any]) -> Dict[str, Any]:
        async with (
            aiohttp.ClientSession() as session,
            session.post(f"{self.base_url}/rewards/claim", json=claims_payload) as rep,
        ):
            if not rep.ok:
                raise RuntimeError(rep.reason)
            return await rep.json()
