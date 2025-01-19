from typing import List, Optional, Tuple

import aiomisc

from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import encode_puzzle_hash
from chia.rpc.wallet_request_types import LogIn, GetLoggedInFingerprintResponse
from chia.wallet.trade_record import TradeRecord

from dexie_rewards.config import (
    address_prefix,
    chia_config,
    chia_root,
    self_hostname,
    wallet_rpc_port,
)


class WalletRpcClientService(aiomisc.Service):
    """
    Mediate access to the chia wallet rpc interface
    """

    _conn: WalletRpcClient

    async def start(self) -> None:
        self._conn = await WalletRpcClient.create(
            self_hostname, wallet_rpc_port, chia_root, chia_config
        )

    async def log_in(self, fingerprint: int) -> None:
        await self._conn.log_in(LogIn(fingerprint))

    async def get_logged_in_fingerprint(self) -> GetLoggedInFingerprintResponse:
        res: GetLoggedInFingerprintResponse = (
            await self._conn.get_logged_in_fingerprint()
        )
        return res.fingerprint

    async def stop(self, exc: Optional[Exception] = None) -> None:
        await super().stop(exc)
        self._conn.close()
        await self._conn.await_closed()

    async def get_all_offers(self) -> List[TradeRecord]:
        return await self._conn.get_all_offers(
            include_completed=True,
            exclude_taken_offers=True,
            file_contents=True,
            start=0,
            end=1000,
        )

    async def sign_message_by_puzzle_hash(
        self, puzzle_hash: bytes32, message: str
    ) -> Tuple[str, str, str]:
        address: str = encode_puzzle_hash(puzzle_hash, address_prefix)
        return await self._conn.sign_message_by_address(address, message)

    @property
    def conn(self) -> WalletRpcClient:
        return self._conn
