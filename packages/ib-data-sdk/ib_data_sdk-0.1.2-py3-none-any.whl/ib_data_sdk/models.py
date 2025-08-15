from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .enums import AssetType, BarSize, Duration, DataType


class HistoricalDataRequest(BaseModel):
    """Model for historical data requests."""

    symbol: str = Field(..., description="Symbol to request data for")
    duration: Duration = Field(
        Duration.DAY_1, description="Duration of historical data"
    )
    bar_size: BarSize = Field(BarSize.MIN_5, description="Bar size for the data")
    asset_type: AssetType = Field(AssetType.STK, description="Type of asset")
    exchange: str = Field("SMART", description="Exchange to route the request")
    data_type: DataType = Field(DataType.TRADES, description="Type of data to retrieve")

    # Options specific fields
    expiry: Optional[str] = Field(None, description="Option expiry date (YYYYMMDD)")
    strike: Optional[float] = Field(None, description="Option strike price")
    right: Optional[str] = Field(None, description="Option right (C/P)")

    @validator("symbol")
    def symbol_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty")
        return v.strip().upper()

    @validator("expiry")
    def validate_expiry_format(cls, v):
        if v and len(v) != 8:
            raise ValueError("Expiry must be in YYYYMMDD format")
        return v

    @validator("right")
    def validate_option_right(cls, v):
        if v and v.upper() not in ["C", "P", "CALL", "PUT"]:
            raise ValueError("Right must be C, P, CALL, or PUT")
        return v.upper() if v else v


class HistoricalDataResponse(BaseModel):
    """Model for historical data responses."""

    request: HistoricalDataRequest
    data: list[dict[str, any]]
    retrieved_at: datetime = Field(default_factory=datetime.now)
    record_count: int = Field(..., description="Number of records retrieved")

    class Config:
        arbitrary_types_allowed = True
