from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint32
from chia.wallet.trading.offer import Offer

from dexie_rewards.config import dexie_api_url, dexie_blue, dexie_url
from dexie_rewards.services.database import DatabaseService
from dexie_rewards.services.wallet_rpc_client import WalletRpcClientService
from dexie_rewards.services.dexie_api import Api, get_dexie_bs58_offer_hash
from dexie_rewards.types.offer_reward import OfferReward


async def create_claims(
    wallet_rpc_client: WalletRpcClientService,
    offers_rewards: List[OfferReward],
    target_puzzle_hash: Optional[bytes32],
) -> List[Any]:
    timestamp = int(time.time())
    claims = []
    for offer_reward in offers_rewards:
        (
            public_key,
            signature,
            signing_mode,
        ) = await sign_claim(
            wallet_rpc_client,
            offer_reward.offer_id,
            timestamp,
            offer_reward.maker_puzzle_hash,
            target_puzzle_hash,
        )

        # return offer hash, signature, pk, and puzzle hash
        claim_info = {
            "offer_id": offer_reward.offer_id,
            "signature": signature,
            "public_key": public_key,
            "timestamp": timestamp,
        }
        claims.append(claim_info)
    return claims


async def get_offers_with_claimable_rewards(
    db: DatabaseService,
    wallet_rpc_client: WalletRpcClientService,
    synced_fingerprint: int,
    console: Console = Console(),
) -> List[Dict[str, Any]]:
    try:
        offers = await wallet_rpc_client.get_all_offers()

        values: List[Tuple[str, str, uint32]] = []
        for offer in offers:
            offer_id = get_dexie_bs58_offer_hash(Offer.from_bytes(offer.offer))
            values.append((offer.trade_id.hex(), offer_id, offer.status))

        num_new_offers = await db.insert_new_offers(values)
        console.print(f"{num_new_offers} new offers", style="bold green")

        num_updated_offers = await db.update_offers_inactive(values)
        console.print(f"{num_updated_offers} updated offers", style="bold green")

        # check offers with claimable rewards
        claimable_offers: List[str] = await db.get_claimable_offers()
        console.print(f"{len(claimable_offers)} claimable offers", style="bold green")

        result: Dict[str, Any] = await Api(
            dexie_api_url
        ).get_offers_with_claimable_rewards(list(claimable_offers))

        # update ts_check
        await db.update_offers_ts_checked(values)

        if not result["success"]:
            Console(stderr=True, style="bold red").print("error getting rewards")
            return []

        # update has_rewards
        num_has_rewards = await db.update_offers_rewards(
            True, list(map(lambda o: o["id"], result["offers"]))
        )
        console.print(f"{num_has_rewards} offers with rewards", style="bold green")

        return result["offers"] if result["success"] else []
    except Exception as e:
        console.print("error getting offers with rewards", style="bold red")
        traceback_string = traceback.format_exc()
        console.print(traceback_string)
        console.print(e)
        return []


async def sign_claim(
    wallet_rpc_client: WalletRpcClientService,
    offer_id: str,
    timestamp: int,
    maker_puzzle_hash: bytes32,
    target_puzzle_hash: Optional[bytes32],
) -> Tuple[str, str, str]:
    message = (
        f"Claim dexie liquidity rewards for offer {offer_id} ({timestamp})"
        if target_puzzle_hash is None
        else (
            f"Claim dexie liquidity rewards for offer {offer_id} to {target_puzzle_hash} ({timestamp})"
        )
    )
    return await wallet_rpc_client.sign_message_by_puzzle_hash(
        maker_puzzle_hash, message
    )


async def claim_rewards(claims_payload: Any) -> Dict[str, Any]:
    result = await Api(dexie_api_url).claim_rewards(claims_payload)
    return result


def display_rewards(offers_rewards: List[OfferReward]) -> None:
    console = Console()
    num_offers = len(offers_rewards)

    if num_offers == 0:
        console.print("No rewards to claim", style="bold red")
        return

    console.print(Text(f"Found {num_offers} offers with total rewards"))

    table = Table(
        box=box.ROUNDED,
        show_footer=False,
    )

    table.add_column(
        "Offer ID",
        justify="center",
        no_wrap=True,
    )
    table.add_column("Rewards", justify="right")
    table.add_column("CAT", justify="center")

    for offer_reward in offers_rewards:
        offer_hash = Text(offer_reward.offer_id)
        offer_hash.stylize(
            f"{dexie_blue} {'strike' if not offer_reward.is_active else 'bold'}"
        )
        offer_hash.stylize(f"link {dexie_url}/offers/{offer_reward.offer_id}")

        for reward in offer_reward.rewards:
            table.add_row(
                offer_hash,
                "{0:0.3f}".format(reward.amount),
                reward.code,
            )

    console.print(table)
