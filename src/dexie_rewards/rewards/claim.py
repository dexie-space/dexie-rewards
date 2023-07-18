from io import StringIO
from rich.console import Console
from rich.prompt import Confirm
from typing import Any, List, Optional
import asyncio
import json
import rich_click as click
import traceback

from blspy import AugSchemeMPL, G1Element, G2Element, PrivateKey

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash

from ..config import dexie_blue
from ..services import dexie_db as dexie_db
from ..utils import wait_for_synced_wallet
from .utils import (
    claim_rewards,
    create_claims,
    display_rewards,
    get_offers_with_claimable_rewards,
)
from ..types.offer_reward import OfferReward


class ChiaWalletAddressParamType(click.ParamType):
    name = "address"

    def convert(self, value, param, ctx):
        try:
            puzzle_hash: bytes32 = decode_puzzle_hash(value)
            return puzzle_hash
        except ValueError:
            self.fail(f"Invalid Chia Wallet Address: {value}", param, ctx)


@click.command("claim", short_help="Claim all offers with dexie rewards")
@click.option(
    "-f",
    "--fingerprint",
    required=False,
    help="Set the fingerprint to specify which wallet to use",
    type=int,
)
@click.option(
    "-vo",
    "--verify-only",
    "verify_only",
    help="Only verify the claim, don't actually claim",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "-y",
    "--yes",
    "skip_confirm",
    help="Skip claim confirmation",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "-v",
    "--verbose",
    "verbose",
    help="Display verbose output",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    "target_puzzle_hash",
    help="Specify a target address to claim rewards to",
    type=ChiaWalletAddressParamType(),
    required=False,
)
@click.option(
    "-co",
    "--completed-only",
    help="Only claim rewards for completed and cancelled offers",
    is_flag=True,
    default=False,
    show_default=True,
)
def claim_cmds(
    fingerprint: Optional[int],
    verify_only: bool,
    skip_confirm: bool,
    verbose: bool,
    target_puzzle_hash: Optional[bytes32],
    completed_only: bool,
) -> None:
    asyncio.run(
        claim_cmds_async(
            fingerprint,
            verify_only,
            skip_confirm,
            verbose,
            target_puzzle_hash,
            completed_only,
        )
    )


async def claim_cmds_async(
    fingerprint: Optional[int],
    verify_only: bool,
    skip_confirm: bool,
    verbose: bool,
    target_puzzle_hash: Optional[bytes32],
    completed_only: bool,
) -> None:
    try:
        console = Console(file=StringIO()) if not verbose else Console()

        synced_fingerprint = await wait_for_synced_wallet(fingerprint)
        await dexie_db.create_db(synced_fingerprint)

        offers_rewards_dict = await get_offers_with_claimable_rewards(
            synced_fingerprint, console
        )

        offers_rewards = list(
            filter(
                (lambda o: not o.is_active) if completed_only else (lambda _: True),
                map(OfferReward.from_json_dict, offers_rewards_dict),
            )
        )

        if len(offers_rewards) == 0:
            console.print("No rewards to claim", style="bold red")
            return

        display_rewards(offers_rewards)

        if not skip_confirm:
            if not Confirm.ask(f"Claim all?"):
                return

        claims = await create_claims(offers_rewards, target_puzzle_hash)
        ret: Any = {"claims": claims}
        if target_puzzle_hash is not None:
            ret["target_puzzle_hash"] = target_puzzle_hash.hex()

        if verify_only:
            ret["verify_only"] = True

        if verbose:
            if target_puzzle_hash is not None:
                console.print(
                    f"target puzzle hash:",
                    style=f"bold {dexie_blue} underline",
                )
                console.print(f"0x{target_puzzle_hash.hex()}")

            console.print(
                "\nclaims request payload:", style=f"bold {dexie_blue} underline"
            )
            console.print_json(json.dumps(ret, indent=4))

        result = await claim_rewards(ret)

        if verbose or verify_only:
            console.print("\nclaims result:", style=f"bold {dexie_blue} underline")
            if verbose:
                console.print_json(json.dumps(result, indent=4))
            else:
                console.print("\nsuccess", style="bold green")

        if result["success"] and not verify_only:
            await dexie_db.update_offers_rewards(
                synced_fingerprint, False, list(result["verified_amount"].keys())
            )

    except Exception as e:
        console.print("Error claiming rewards", style="bold red")
        traceback_string = traceback.format_exc()
        console.print(traceback_string)
        console.print(e)
