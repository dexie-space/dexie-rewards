from typing import List, Tuple

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.bech32m import encode_puzzle_hash
from chia.wallet.trade_record import TradeRecord

from ..config import (
    address_prefix,
    chia_config,
    chia_root,
    self_hostname,
    wallet_rpc_port,
)
from ..decorators.with_wallet_rpc_client import with_wallet_rpc_client


@with_wallet_rpc_client(self_hostname, wallet_rpc_port, chia_root, chia_config)
async def get_logged_in_fingerprint(
    wallet_rpc_client: WalletRpcClient,
) -> int:
    return await wallet_rpc_client.get_logged_in_fingerprint()


@with_wallet_rpc_client(self_hostname, wallet_rpc_port, chia_root, chia_config)
async def log_in(wallet_rpc_client: WalletRpcClient, fingerprint: int) -> None:
    await wallet_rpc_client.log_in(fingerprint)


@with_wallet_rpc_client(self_hostname, wallet_rpc_port, chia_root, chia_config)
async def get_synced(wallet_rpc_client: WalletRpcClient) -> bool:
    return await wallet_rpc_client.get_synced()


@with_wallet_rpc_client(self_hostname, wallet_rpc_port, chia_root, chia_config)
async def get_all_offers(wallet_rpc_client: WalletRpcClient) -> List[TradeRecord]:
    return await wallet_rpc_client.get_all_offers(
        include_completed=True, exclude_taken_offers=True, file_contents=True, start=0, end=1000
    )


@with_wallet_rpc_client(self_hostname, wallet_rpc_port, chia_root, chia_config)
async def sign_message_by_puzzle_hash(
    wallet_rpc_client: WalletRpcClient, puzzle_hash: bytes32, message: str
) -> Tuple[str, str, str]:
    address: str = encode_puzzle_hash(puzzle_hash, address_prefix)
    return await wallet_rpc_client.sign_message_by_address(address, message)
