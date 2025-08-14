from abc import ABC, abstractmethod
from typing import Union
from ibapi.common import BarData, TickAttrib
from .enums import DataType


class DataProcessor(ABC):
    """Abstract base class for data processors."""

    @abstractmethod
    def process_bar_data(
        self,
        price: Union[BarData, TickAttrib],
    ) -> dict[str, any]:
        """Process incoming bar data and return formatted record."""
        pass

    @abstractmethod
    def get_data_type(self) -> DataType:
        """Return the data type this processor handles."""
        pass


class TradesDataProcessor(DataProcessor):
    """Processor for TRADES data type."""

    def process_bar_data(
        self,
        price: Union[BarData, TickAttrib],
    ) -> dict[str, any]:
        return {
            "date": price.date,
            "open": float(price.open),
            "high": float(price.high),
            "low": float(price.low),
            "close": float(price.close),
            "volume": int(price.volume),
        }

    def get_data_type(self) -> DataType:
        return DataType.TRADES


class BidAskDataProcessor(DataProcessor):
    """Processor for BID_ASK data type."""

    def process_bar_data(
        self,
        price: Union[BarData, TickAttrib],
    ) -> dict[str, any]:
        return {
            "date": price.date,
            "bid_price": float(price.open),
            "ask_price": float(price.high),
            "bid_size": int(price.low),
            "ask_size": int(price.close),
        }

    def get_data_type(self) -> DataType:
        return DataType.BID_ASK


class MidpointDataProcessor(DataProcessor):
    """Processor for MIDPOINT data type."""

    def process_bar_data(
        self,
        price: Union[BarData, TickAttrib],
    ) -> dict[str, any]:
        return {
            "date": price.date,
            "midpoint": float((price.open + price.high) / 2),
            "volume": int(price.volume),
        }

    def get_data_type(self) -> DataType:
        return DataType.MIDPOINT


class DataProcessorFactory:
    """Factory for creating data processors."""

    _processors = {
        DataType.TRADES: TradesDataProcessor,
        DataType.BID_ASK: BidAskDataProcessor,
        DataType.MIDPOINT: MidpointDataProcessor,
    }

    @classmethod
    def create_processor(
        cls,
        data_type: DataType,
    ) -> DataProcessor:
        """Create appropriate processor for the given data type."""
        processor_class = cls._processors.get(data_type)
        if not processor_class:
            raise ValueError(f"Unsupported data type: {data_type}")
        return processor_class()

    @classmethod
    def register_processor(
        cls,
        data_type: DataType,
        processor_class: type,
    ):
        """Register a new processor type."""
        cls._processors[data_type] = processor_class
