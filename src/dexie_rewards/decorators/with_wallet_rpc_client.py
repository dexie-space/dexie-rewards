from pathlib import Path
from rich.console import Console
import sys
from typing import Any, Dict

from chia.util.ints import uint16
from chia.rpc.wallet_rpc_client import WalletRpcClient


async def run_rpc(rpc_client, f, *args, **kwargs):  # type: ignore
    try:
        result = await f(rpc_client, *args, **kwargs)
    except Exception:
        raise
    finally:
        rpc_client.close()
        await rpc_client.await_closed()
    return result


def with_wallet_rpc_client(self_hostname: str, rpc_port: uint16, chia_root: Path, chia_config: Dict[str, Any]):  # type: ignore
    def _with_wallet_rpc_client(f):  # type: ignore
        async def with_rpc_client(*args, **kwargs):  # type: ignore
            try:
                rpc_client = await WalletRpcClient.create(
                    self_hostname, rpc_port, chia_root, chia_config
                )
                return await run_rpc(rpc_client, f, *args, **kwargs)  # type: ignore
            except Exception:
                Console(stderr=True, style="bold red").print(
                    "Unable to connect to wallet"
                )
                sys.exit(1)

        return with_rpc_client

    return _with_wallet_rpc_client
