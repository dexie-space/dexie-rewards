from datetime import datetime, timezone
import pytest

from dexie_rewards.types.utils import to_datetime, from_datetime


class TestTypes:
    def test_to_datetime(self) -> None:
        assert to_datetime("2023-04-21T01:36:13.325Z") == datetime(
            2023, 4, 21, 1, 36, 13, 325000
        )

    def test_from_datetime(self) -> None:
        assert (
            from_datetime(datetime(2023, 4, 21, 1, 36, 13, 325000))
            == "2023-04-21T01:36:13.325Z"
        )
