import os
import time
import logging
from threading import Thread, Event
from typing import Optional
import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper, iswrapper
from ibapi.common import BarData, TickAttrib

from .exceptions import ConnectionError, DataRequestError, TimeoutError, ValidationError
from .models import HistoricalDataRequest, HistoricalDataResponse
from .processors import DataProcessorFactory
from .contracts import ContractHandler


logger = logging.getLogger(__name__)


class IBDataClient(EClient, EWrapper):
    """
    Main client for retrieving historical data from Interactive Brokers.

    This client provides a clean interface for connecting to IB and retrieving
    historical market data with support for multiple data types and automatic
    data processing.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        client_id: Optional[int] = None,
        timeout: int = 30,
    ):
        """
        Initialize the IB Data Client.

        Args:
            host: IB Gateway/TWS host (default: from TWS_HOST env var)
            port: IB Gateway/TWS port (default: from TWS_PORT env var)
            client_id: Client ID for connection (default: from TWS_CLIENT_ID env var)
            timeout: Connection timeout in seconds
        """
        EClient.__init__(self, self)

        # Connection parameters
        self.host = host or os.getenv("TWS_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("TWS_PORT", "7497"))
        self.client_id = client_id or int(os.getenv("TWS_CLIENT_ID", "1"))
        self.timeout = timeout

        # Connection state
        self.next_order_id = None
        self.connected_event = Event()
        self.is_connected = False

        # Data handling
        self.current_request: Optional[HistoricalDataRequest] = None
        self.current_processor = None
        self.records: list[dict[str, any]] = []
        self.data_ready_event = Event()

    def connect_to_ib(self) -> bool:
        """
        Connect to Interactive Brokers.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to IB at {self.host}:{self.port}")

            self.connect(
                self.host,
                self.port,
                self.client_id,
            )

            # Start the socket thread
            thread = Thread(target=self.run, daemon=True)
            thread.start()

            # Wait for connection with timeout
            if not self.connected_event.wait(timeout=self.timeout):
                raise ConnectionError(
                    f"Connection timeout after {self.timeout} seconds"
                )

            self.is_connected = True

            logger.info("Successfully connected to IB")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to IB: {e}")

            raise ConnectionError(f"Failed to connect to IB: {e}")

    def disconnect_from_ib(self):
        """Disconnect from Interactive Brokers."""
        if self.isConnected():
            logger.info("Disconnecting from IB")

            self.disconnect()
            self.is_connected = False

    def get_historical_data(
        self,
        request: HistoricalDataRequest,
        timeout: int = 30,
    ) -> HistoricalDataResponse:
        """
        Get historical data for the given request.

        Args:
            request: Historical data request parameters
            timeout: Request timeout in seconds

        Returns:
            HistoricalDataResponse: Response containing the retrieved data

        Raises:
            ValidationError: If request validation fails
            DataRequestError: If data request fails
            TimeoutError: If request times out
        """
        # Validate request
        try:
            request.dict()  # This will run Pydantic validation

        except Exception as e:
            raise ValidationError(f"Invalid request: {e}")

        # Ensure connection
        if not self.is_connected:
            self.connect_to_ib()

        # Reset state for new request
        self.current_request = request
        self.current_processor = DataProcessorFactory.create_processor(
            request.data_type
        )
        self.records.clear()
        self.data_ready_event.clear()

        try:
            # Create contract and make request
            contract = ContractHandler.create_contract_from_request(request)

            logger.info(f"Requesting historical data for {request.symbol}")

            self.reqHistoricalData(
                reqId=1,
                contract=contract,
                endDateTime="",
                durationStr=request.duration.value,
                barSizeSetting=request.bar_size.value,
                whatToShow=request.data_type.value,
                useRTH=1,
                formatDate=1,
                keepUpToDate=False,
                chartOptions=[],
            )

            # Wait for data with timeout
            if not self.data_ready_event.wait(timeout=timeout):
                raise TimeoutError(f"Data request timed out after {timeout} seconds")

            # Create response
            response = HistoricalDataResponse(
                request=request,
                data=self.records.copy(),
                record_count=len(self.records),
            )

            logger.info(f"Retrieved {len(self.records)} records for {request.symbol}")

            return response

        except Exception as e:
            if isinstance(e, (ValidationError, TimeoutError)):
                raise

            raise DataRequestError(f"Failed to retrieve data: {e}")

    def get_historical_data_as_dataframe(
        self,
        request: HistoricalDataRequest,
        timeout: int = 30,
    ) -> pd.DataFrame:
        """
        Get historical data as a pandas DataFrame.

        Args:
            request: Historical data request parameters
            timeout: Request timeout in seconds

        Returns:
            pd.DataFrame: DataFrame with historical data
        """
        response = self.get_historical_data(request, timeout)

        if not response.data:
            return pd.DataFrame()

        df = pd.DataFrame(response.data)
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

        return df

    # IB API callback methods
    def nextValidId(
        self,
        order_id: int,
    ):
        """Callback when next valid order ID is received."""
        logger.debug(f"Next valid order ID: {order_id}")
        self.next_order_id = order_id
        self.connected_event.set()

    def error(
        self,
        req_id: int,
        error_code: int,
        error_string: str,
    ):
        """Handle IB API errors."""
        if error_code in [2104, 2106]:
            logger.info("Market data farm connection is OK")
        elif error_code == 321:
            logger.warning("Market data farm connection is bad")
        elif error_code == 502:
            logger.error("Historical Market Data Service error")
        else:
            logger.error(f"IB Error {error_code}: {error_string}")

    @iswrapper
    def historicalData(
        self,
        req_id: int,
        price: BarData,
    ):
        """Process incoming historical data."""
        if self.current_processor:
            record = self.current_processor.process_bar_data(price)
            self.records.append(record)
            logger.debug(f"Received data point, total: {len(self.records)}")

    @iswrapper
    def historicalDataEnd(
        self,
        req_id: int,
        start: str,
        end: str,
    ):
        """Called when historical data request is complete."""
        logger.info(
            f"Historical data request complete. Retrieved {len(self.records)} records"
        )
        self.data_ready_event.set()
