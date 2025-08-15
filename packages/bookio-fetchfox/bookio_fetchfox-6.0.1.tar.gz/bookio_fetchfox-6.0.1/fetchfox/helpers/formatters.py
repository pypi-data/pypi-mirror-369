from datetime import datetime


def timestamp(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00"),
    )
