from pathlib import Path
from typing import Any, Optional

import aiomisc
import aiosqlite
import asyncio

from ..abc import DatabaseServiceBase
from ..types.offers import OfferTableMixin
from ..config import dexie_db_path
from .wallet_rpc_client import WalletRpcClientService


class DatabaseService(aiomisc.Service, OfferTableMixin, DatabaseServiceBase):
    """
    Mediate access to the database
    """

    _conn: aiosqlite.Connection
    _fingerprint: Optional[int]
    _location: Path
    _wallet_rpc_client: WalletRpcClientService

    def __init__(
        self,
        wallet_rpc_client: WalletRpcClientService,
        fingerprint: Optional[int],
        state_dir: Optional[Path] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._wallet_rpc_client = wallet_rpc_client
        self._fingerprint = fingerprint

        if state_dir is None:
            self._location = Path(dexie_db_path)
        else:
            self._location = state_dir

        self._location.mkdir(parents=True, exist_ok=True)

    async def start(self) -> None:
        if self._fingerprint is None:
            # make sure wallet rpc client is created
            while not self._wallet_rpc_client.start_event.is_set():
                await asyncio.sleep(1)

            self._fingerprint = (
                await self._wallet_rpc_client.conn.get_logged_in_fingerprint()
            )

        db_location = self._location.joinpath(f"dexie-{self._fingerprint}.db")

        self._conn = await aiosqlite.connect(db_location)
        self._conn.row_factory = aiosqlite.Row
        await self._start_hook()

    async def stop(self, exception: Optional[Exception] = None) -> None:
        await super().stop(exception)
        await self._conn.close()

    @property
    def conn(self) -> aiosqlite.Connection:
        return self._conn
