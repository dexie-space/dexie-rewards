import aiomisc
from io import StringIO
import json
from rich.console import Console
import rich_click as click
import traceback
from typing import Optional

from dexie_rewards.rewards.utils import (
    display_rewards,
    get_offers_with_claimable_rewards,
)
from dexie_rewards.services.database import DatabaseService
from dexie_rewards.services.wallet_rpc_client import WalletRpcClientService
from dexie_rewards.types.offer_reward import OfferReward
from dexie_rewards.utils import wait_for_synced_wallet


@click.command("list", short_help="List all offers with dexie rewards")
@click.option(
    "-f",
    "--fingerprint",
    required=False,
    help="Set the fingerprint to specify which wallet to use",
    type=int,
)
@click.option(
    "-j",
    "--json",
    "as_json",
    help="Displays offers as JSON",
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
def list_cmds(fingerprint: Optional[int], as_json: bool, verbose: bool) -> None:
    console = Console(file=StringIO()) if as_json or (not verbose) else Console()
    wallet_rpc_client = WalletRpcClientService()
    db = DatabaseService(wallet_rpc_client, fingerprint)
    aiomisc.run(
        list_cmds_async(db, wallet_rpc_client, console, fingerprint, as_json, verbose),
        wallet_rpc_client,
        db,
    )


async def list_cmds_async(
    db: DatabaseService,
    wallet_rpc_client: WalletRpcClientService,
    console: Console,
    fingerprint: Optional[int],
    as_json: bool,
    verbose: bool,
) -> None:
    try:
        synced_fingerprint = await wait_for_synced_wallet(
            wallet_rpc_client, fingerprint, console
        )

        offers_rewards_dict = await get_offers_with_claimable_rewards(
            db, wallet_rpc_client, synced_fingerprint, console
        )
        if as_json:
            click.echo(json.dumps(offers_rewards_dict))
        else:
            offers_rewards = list(map(OfferReward.from_json_dict, offers_rewards_dict))
            display_rewards(offers_rewards)

    except Exception as e:
        console.print("Error listing rewards", style="bold red")
        traceback_string = traceback.format_exc()
        console.print(traceback_string)
        console.print(e)
