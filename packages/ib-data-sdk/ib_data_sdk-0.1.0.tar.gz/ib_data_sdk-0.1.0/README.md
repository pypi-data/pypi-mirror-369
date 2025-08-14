# IB Data SDK

A Python SDK for retrieving historical market data from Interactive Brokers with a clean, extensible interface.

## Features

- 🚀 **Easy to use**: Simple, intuitive API for data retrieval
- 🔧 **Extensible**: Plugin architecture for custom data processors  
- 📊 **Pandas integration**: Built-in DataFrame support
- 🛡️ **Type safe**: Full type hints and Pydantic validation
- 📱 **CLI included**: Command-line interface for quick data retrieval
- 🏗️ **Production ready**: Proper error handling, logging, and testing

## Installation

```bash
pip install ib-data-sdk
```

For development:
```bash
pip install ib-data-sdk[dev]
```

## Quick Start

### Environment Setup

Set up your IB connection parameters:

```bash
export TWS_HOST=127.0.0.1
export TWS_PORT=7497  # or 7496 for live trading
export TWS_CLIENT_ID=1
```

### Basic Usage

```python
from ib_data_sdk import IBDataClient, HistoricalDataRequest
from ib_data_sdk.enums import Duration, BarSize, DataType

# Create client
client = IBDataClient()

# Create request
request = HistoricalDataRequest(
    symbol="AAPL",
    duration=Duration.DAY_1, 
    bar_size=BarSize.MIN_5,
    data_type=DataType.TRADES
)

# Get data as DataFrame
df = client.get_historical_data_as_dataframe(request)
print(df.head())

# Clean up
client.disconnect_from_ib()
```

### Using the CLI

```bash
# Get daily AAPL data
ib-data get-data AAPL --duration DAY_1 --bar-size MIN_5

# Save to file
ib-data get-data AAPL --output aapl_data.csv

# List available options
ib-data list-enums
```

## Advanced Usage

### Custom Data Processors

```python
from ib_data_sdk import DataProcessor, DataType

class VolumeWeightedDataProcessor(DataProcessor):
    def process_bar_data(self, price):
        return {
            "date": price.date,
            "vwap": (price.open + price.close) / 2 * price.volume,
            "volume": price.volume,
        }
    
    def get_data_type(self):
        return DataType.TRADES

# Register the processor
from ib_data_sdk.processors import DataProcessorFactory
DataProcessorFactory.register_processor(DataType.TRADES, VolumeWeightedDataProcessor)
```

### Options Data

```python
request = HistoricalDataRequest(
    symbol="AAPL",
    asset_type=AssetType.OPT,
    expiry="20240119",
    strike=150.0,
    right="C"  # Call option
)

df = client.get_historical_data_as_dataframe(request)
```

### Error Handling

```python
from ib_data_sdk.exceptions import ConnectionError, DataRequestError, TimeoutError

try:
    df = client.get_historical_data_as_dataframe(request)
except ConnectionError:
    print("Failed to connect to IB")
except DataRequestError as e:
    print(f"Data request failed: {e}")
except TimeoutError:
    print("Request timed out")
```

## API Reference

### Classes

- **IBDataClient**: Main client class for data retrieval
- **HistoricalDataRequest**: Request model with validation
- **HistoricalDataResponse**: Response model with metadata
- **DataProcessor**: Abstract base for custom processors

### Enums

- **AssetType**: STK, OPT, FUT, CASH, IND
- **BarSize**: 1 sec to 1 month intervals
- **Duration**: 1 D to 2 Y periods  
- **DataType**: TRADES, BID_ASK, MIDPOINT, etc.

## Development

### Setup

```bash
git clone https://github.com/quantphantom/ib-data-sdk
cd ib-data-sdk
pip install -e .[dev]
pre-commit install
```

### Testing

```bash
pytest tests/ -v --cov=src/ib_data_sdk
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 **Documentation**: https://ib-data-sdk.readthedocs.io/
- 🐛 **Issues**: https://github.com/quantphantom/ib-data-sdk/issues
- 💬 **Discussions**: https://github.com/quantphantom/ib-data-sdk/discussions

## Disclaimer

This project is not affiliated with Interactive Brokers. Use at your own risk.
Trading
