from datetime import datetime


def to_datetime(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str[:-1])


def from_datetime(date: datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
