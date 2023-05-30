from datetime import datetime
import sqlite3
from typing import Any, Dict, List, Tuple

from ..config import dexie_db_path
from ..decorators.with_db_connection import get_full_db_path, with_db_connection

CREATE_OFFERS = """
    CREATE TABLE IF NOT EXISTS offers (
        trade_id TEXT PRIMARY KEY,
        offer_id TEXT NOT NULL,
        has_rewards INTEGER NOT NULL DEFAULT 0,
        ts_found TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ts_checked TIMESTAMP,
        ts_inactive TIMESTAMP
    );
"""


async def create_db(fingerprint: int) -> None:
    db = sqlite3.connect(get_full_db_path(dexie_db_path, fingerprint))
    db.execute(CREATE_OFFERS)
    db.close()


@with_db_connection(dexie_db_path)  # type: ignore
async def insert_new_offers(conn: Any, offers: List[Tuple[str, str, int]]) -> int:
    # insert offers if needed
    async with conn.cursor() as cursor:
        sql = "INSERT OR IGNORE INTO offers (trade_id, offer_id, ts_inactive) VALUES (?, ?, ?)"
        values = [
            (trade_id, offer_id, None if status == 0 else datetime.now())
            for trade_id, offer_id, status in offers
        ]
        result = await cursor.executemany(sql, values)

    await conn.commit()
    return result.rowcount


@with_db_connection(dexie_db_path)  # type: ignore
async def update_offers_inactive(conn: Any, offers: List[Tuple[str, str, int]]) -> int:
    counts = 0
    for trade_id, _, status in offers:
        if status == 0:
            continue

        # update ts_inactive
        # for offers that are no longer active (completed or cancelled)
        # and ts_inactive is null
        ts_inactive = datetime.now()
        async with conn.cursor() as cursor:
            sql = """
            UPDATE offers 
            SET ts_inactive = ? 
            WHERE trade_id = ? 
            AND ts_inactive IS NULL"""
            result = await cursor.execute(sql, (ts_inactive, trade_id))
            counts += result.rowcount

    await conn.commit()
    return counts


@with_db_connection(dexie_db_path)  # type: ignore
async def update_offers_rewards(conn: Any, has_rewards: bool, offers: List[str]) -> int:
    counts = 0
    for offer_id in offers:
        # update has_rewards
        async with conn.cursor() as cursor:
            sql = """
            UPDATE offers 
            SET has_rewards = ?
            WHERE offer_id = ?"""
            result = await cursor.execute(sql, (has_rewards, offer_id))
            counts += result.rowcount

    await conn.commit()
    return counts


@with_db_connection(dexie_db_path)  # type: ignore
async def update_offers_ts_checked(
    conn: Any, offers: List[Tuple[str, str, int]]
) -> int:
    for trade_id, _, _ in offers:
        ts_checked = datetime.now()
        async with conn.cursor() as cursor:
            sql = """
            UPDATE offers 
            SET ts_checked = ?
            WHERE trade_id = ?"""
            result = await cursor.execute(sql, (ts_checked, trade_id))

    await conn.commit()


@with_db_connection(dexie_db_path)  # type: ignore
async def get_claimable_offers(conn: Any) -> List[str]:
    offer_ids: List[str] = []
    async with conn.execute(
        """
        SELECT offer_id 
        FROM offers 
        WHERE ts_checked IS NULL            -- unchecked offers
        OR ts_inactive IS NULL              -- active offers
        OR (ts_inactive IS NOT NULL 
            AND has_rewards = 1)            -- inactive offers with unclaimed rewards
        OR (ts_inactive IS NOT NULL 
            AND ts_checked < ts_inactive)   -- unchecked inactive offers
        LIMIT 1000
    """
    ) as cursor:
        rows = await cursor.fetchall()
        for row in rows:
            offer_ids.append(row[0])
    return offer_ids
