"""
IB Data SDK - A Python SDK for Interactive Brokers historical data retrieval.

This SDK provides a clean, extensible interface for retrieving historical market data
from Interactive Brokers using their API, with support for multiple data types and
built-in data processing capabilities.
"""

__version__ = "0.1.0"
__author__ = "Lim Yuan Sheng"
__email__ = "yuansheng0424@gmail.com"

from .client import IBDataClient
from .processors import TradesDataProcessor, BidAskDataProcessor, DataProcessor
from .exceptions import (
    IBDataSDKError,
    ConnectionError,
    DataRequestError,
    TimeoutError,
    ValidationError,
)
from .enums import AssetType, BarSize, Duration, DataType
from .models import HistoricalDataRequest, HistoricalDataResponse

__all__ = [
    "IBDataClient",
    "TradesDataProcessor",
    "BidAskDataProcessor",
    "DataProcessor",
    "IBDataSDKError",
    "ConnectionError",
    "DataRequestError",
    "TimeoutError",
    "ValidationError",
    "AssetType",
    "BarSize",
    "Duration",
    "DataType",
    "HistoricalDataRequest",
    "HistoricalDataResponse",
]
