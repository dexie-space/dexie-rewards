import asyncio
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from typing import Optional

from blspy import AugSchemeMPL, G1Element, G2Element, PrivateKey
from chia.cmds.keys_funcs import private_key_for_fingerprint
from chia.consensus.coinbase import create_puzzlehash_for_pk
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint32
from chia.wallet.cat_wallet.cat_utils import CAT_MOD
from chia.wallet.derive_keys import (
    master_sk_to_wallet_sk,
    master_sk_to_wallet_sk_unhardened,
)
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    calculate_synthetic_secret_key,
    DEFAULT_HIDDEN_PUZZLE_HASH,
)

from .services import wallet_rpc_client as wallet_rpc_client


async def is_wallet_synced(fingerprint: int) -> bool:
    await wallet_rpc_client.log_in(fingerprint)

    is_synced = await wallet_rpc_client.get_synced()
    if is_synced:
        return True

    return False


async def wait_for_synced_wallet(
    fingerprint: Optional[int], console: Console = Console()
) -> int:
    if fingerprint is None:
        fingerprint = await wallet_rpc_client.get_logged_in_fingerprint()
        console.print(f"Using wallet with fingerprint: {fingerprint}")

    await wallet_rpc_client.log_in(fingerprint)
    syncing_wallet_progress = Progress(
        TextColumn("{task.description}"),
        SpinnerColumn("dots8Bit"),
        TimeElapsedColumn(),
        transient=True,
    )

    syncing_wallet_task_id = syncing_wallet_progress.add_task(
        f"[bold bright_cyan]Syncing {fingerprint}", total=None
    )

    with syncing_wallet_progress:
        while True:
            if await is_wallet_synced(fingerprint):
                break
            await asyncio.sleep(2)

    return fingerprint
