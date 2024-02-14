from datetime import datetime
from typing import List, Tuple

from chia.util.ints import uint32

from dexie_rewards.abc import DatabaseServiceBase


class OfferTableMixin(DatabaseServiceBase):
    async def _start_hook(self) -> None:
        await super()._start_hook()
        fields = ",".join(
            [
                "trade_id TEXT PRIMARY KEY",
                "offer_id TEXT NOT NULL",
                "has_rewards INTEGER NOT NULL DEFAULT 0",
                "ts_found TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
                "ts_checked TIMESTAMP",
                "ts_inactive TIMESTAMP",
            ]
        )
        await self.conn.execute(f"CREATE TABLE IF NOT EXISTS offers ({fields})")

    async def insert_new_offers(self, offers: List[Tuple[str, str, uint32]]) -> int:
        async with self.conn.cursor() as cursor:
            sql = "INSERT OR IGNORE INTO offers (trade_id, offer_id, ts_inactive) VALUES (?, ?, ?)"
            values = [
                (trade_id, offer_id, None if status == 0 else datetime.now())
                for trade_id, offer_id, status in offers
            ]
            result = await cursor.executemany(sql, values)
        await self.conn.commit()
        return result.rowcount

    async def update_offers_inactive(
        self, offers: List[Tuple[str, str, uint32]]
    ) -> int:
        counts = 0
        for trade_id, _, status in offers:
            if status == 0:
                continue

            # update ts_inactive
            # for offers that are no longer active (completed or cancelled)
            # and ts_inactive is null
            ts_inactive = datetime.now()
            async with self.conn.cursor() as cursor:
                sql = """
                UPDATE offers
                SET ts_inactive = ?
                WHERE trade_id = ?
                AND ts_inactive IS NULL"""
                result = await cursor.execute(sql, (ts_inactive, trade_id))
                counts += result.rowcount

        await self.conn.commit()
        return counts

    async def update_offers_rewards(self, has_rewards: bool, offers: List[str]) -> int:
        counts = 0
        for offer_id in offers:
            # update has_rewards
            async with self.conn.cursor() as cursor:
                sql = """
                UPDATE offers
                SET has_rewards = ?
                WHERE offer_id = ?"""
                result = await cursor.execute(sql, (has_rewards, offer_id))
                counts += result.rowcount

        await self.conn.commit()
        return counts

    async def update_offers_ts_checked(
        self, offers: List[Tuple[str, str, uint32]]
    ) -> int:
        count_updated = 0
        for trade_id, _, _ in offers:
            ts_checked = datetime.now()
            async with self.conn.cursor() as cursor:
                sql = """
                UPDATE offers
                SET ts_checked = ?
                WHERE trade_id = ?"""
                await cursor.execute(sql, (ts_checked, trade_id))
            count_updated += 1

        await self.conn.commit()
        return count_updated

    async def get_claimable_offers(self) -> List[str]:
        offer_ids: List[str] = []
        async with self.conn.execute(
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
