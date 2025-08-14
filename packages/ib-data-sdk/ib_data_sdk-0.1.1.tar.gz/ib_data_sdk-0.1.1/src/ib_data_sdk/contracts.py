from ibapi.contract import Contract
from .enums import AssetType
from .models import HistoricalDataRequest


class ContractHandler:
    """Utility class for creating IB contracts."""

    @staticmethod
    def create_contract_from_request(request: HistoricalDataRequest) -> Contract:
        """Create IB contract from request model."""
        contract = Contract()
        contract.symbol = request.symbol
        contract.secType = request.asset_type.value
        contract.exchange = request.exchange
        contract.currency = "USD"  # Default to USD

        # Handle options
        if request.asset_type == AssetType.OPT:
            if not all([request.expiry, request.strike, request.right]):
                raise ValueError("Options require expiry, strike, and right")

            contract.lastTradeDateOrContractMonth = request.expiry
            contract.strike = request.strike
            contract.right = request.right

        return contract
