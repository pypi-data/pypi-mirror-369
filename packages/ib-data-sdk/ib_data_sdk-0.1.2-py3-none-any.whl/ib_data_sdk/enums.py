from enum import StrEnum


class AssetType(StrEnum):
    """Asset types supported by IB."""

    STK = "STK"  # Stock
    OPT = "OPT"  # Option
    FUT = "FUT"  # Future
    CASH = "CASH"  # Currency
    IND = "IND"  # Index


class BarSize(StrEnum):
    """Bar sizes for historical data."""

    SEC_1 = "1 sec"
    SEC_5 = "5 secs"
    SEC_10 = "10 secs"
    SEC_15 = "15 secs"
    SEC_30 = "30 secs"
    MIN_1 = "1 min"
    MIN_2 = "2 mins"
    MIN_3 = "3 mins"
    MIN_5 = "5 mins"
    MIN_10 = "10 mins"
    MIN_15 = "15 mins"
    MIN_20 = "20 mins"
    MIN_30 = "30 mins"
    HOUR_1 = "1 hour"
    HOUR_2 = "2 hours"
    HOUR_3 = "3 hours"
    HOUR_4 = "4 hours"
    HOUR_8 = "8 hours"
    DAY_1 = "1 day"
    WEEK_1 = "1 week"
    MONTH_1 = "1 month"


class Duration(StrEnum):
    """Duration strings for historical data requests."""

    DAY_1 = "1 D"
    DAYS_2 = "2 D"
    DAYS_3 = "3 D"
    DAYS_5 = "5 D"
    WEEK_1 = "1 W"
    WEEKS_2 = "2 W"
    MONTH_1 = "1 M"
    MONTHS_2 = "2 M"
    MONTHS_3 = "3 M"
    MONTHS_6 = "6 M"
    YEAR_1 = "1 Y"
    YEARS_2 = "2 Y"


class DataType(StrEnum):
    """Types of data that can be requested."""

    TRADES = "TRADES"
    BID_ASK = "BID_ASK"
    MIDPOINT = "MIDPOINT"
    BID = "BID"
    ASK = "ASK"
