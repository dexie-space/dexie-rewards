import aiosqlite
from pathlib import Path


def get_full_db_path(db_path: str, fingerprint: int) -> str:
    return f"{db_path}/dexie-{fingerprint}.db"


def with_db_connection(db_path):  # type: ignore
    def _with_db_connection(f):  # type: ignore
        async def with_connection(fingerprint: int, *args, **kwargs):  # type: ignore
            full_db_path = Path(get_full_db_path(db_path, fingerprint))
            conn = await aiosqlite.connect(full_db_path)
            try:
                rv = await f(conn, *args, **kwargs)
            except Exception:
                await conn.rollback()
                raise
            else:
                await conn.commit()
            finally:
                await conn.close()

            return rv

        return with_connection

    return _with_db_connection
