import asyncio
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from typing import Optional

from dexie_rewards.services.wallet_rpc_client import WalletRpcClientService


async def is_wallet_synced(
    wallet_rpc_client: WalletRpcClientService, fingerprint: int
) -> bool:
    await wallet_rpc_client.log_in(fingerprint)

    is_synced = await wallet_rpc_client.conn.get_synced()
    if is_synced:
        return True

    return False


async def wait_for_synced_wallet(
    wallet_rpc_client: WalletRpcClientService,
    fingerprint: Optional[int],
    console: Console = Console(),
) -> int:
    if fingerprint is None:
        fingerprint = await wallet_rpc_client.conn.get_logged_in_fingerprint()
        if fingerprint is None:
            raise Exception("No wallet logged in")
        console.print(f"Using wallet with fingerprint: {fingerprint}")

    await wallet_rpc_client.log_in(fingerprint)
    syncing_wallet_progress = Progress(
        TextColumn("{task.description}"),
        SpinnerColumn("dots8Bit"),
        TimeElapsedColumn(),
        transient=True,
    )

    syncing_wallet_progress.add_task(
        f"[bold bright_cyan]Syncing {fingerprint}", total=None
    )

    with syncing_wallet_progress:
        while True:
            if await is_wallet_synced(wallet_rpc_client, fingerprint):
                break
            await asyncio.sleep(2)

    return fingerprint
