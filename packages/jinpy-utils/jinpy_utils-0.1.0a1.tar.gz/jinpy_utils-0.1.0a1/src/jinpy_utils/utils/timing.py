from datetime import UTC, datetime


def get_current_datetime() -> datetime:
    """Return the current timezone-aware datetime in UTC.

    Returns:
        A `datetime` object with tzinfo set to UTC.
    """
    return datetime.now(UTC)
