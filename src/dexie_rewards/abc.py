from abc import abstractproperty

import aiosqlite


class DatabaseServiceBase:
    @abstractproperty
    def conn(self) -> aiosqlite.Connection:
        ...

    async def _start_hook(self) -> None:
        pass
