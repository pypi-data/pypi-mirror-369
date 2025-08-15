import typer
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import track
from typing import Optional

from .client import IBDataClient
from .models import HistoricalDataRequest
from .enums import (
    AssetType,
    BarSize,
    Duration,
    DataType,
)

app = typer.Typer(
    help="IB Data SDK - Retrieve historical data from Interactive Brokers"
)
console = Console()


@app.command()
def get_data(
    symbol: str = typer.Argument(..., help="Stock symbol to retrieve data for"),
    duration: Duration = typer.Option(
        Duration.DAY_1, help="Duration of data to retrieve"
    ),
    bar_size: BarSize = typer.Option(BarSize.MIN_5, help="Bar size for the data"),
    data_type: DataType = typer.Option(
        DataType.TRADES, help="Type of data to retrieve"
    ),
    output: Optional[str] = typer.Option(None, help="Output file (CSV format)"),
    display: bool = typer.Option(True, help="Display data in terminal"),
):
    """Retrieve historical data for a symbol."""

    console.print(
        f"[bold blue]Retrieving {data_type.value} data for {symbol}[/bold blue]"
    )

    try:
        # Create client and request
        client = IBDataClient()
        request = HistoricalDataRequest(
            symbol=symbol, duration=duration, bar_size=bar_size, data_type=data_type
        )

        # Get data with progress indication
        with console.status("[bold green]Connecting to IB and retrieving data..."):
            df = client.get_historical_data_as_dataframe(request)

        if df.empty:
            console.print("[red]No data retrieved[/red]")
            return

        console.print(f"[green]Successfully retrieved {len(df)} records[/green]")

        # Display data
        if display:
            table = Table(title=f"Historical Data - {symbol}")
            for column in df.columns:
                table.add_column(column)

            # Show first 10 rows
            for idx, row in df.head(10).iterrows():
                table.add_row(*[str(val) for val in row])

            if len(df) > 10:
                table.add_row(*["..." for _ in df.columns])

            console.print(table)

        # Save to file
        if output:
            df.to_csv(output)
            console.print(f"[green]Data saved to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    finally:
        try:
            client.disconnect_from_ib()
        except:
            pass


@app.command()
def list_enums():
    """List available enum values."""

    console.print("[bold blue]Available Asset Types:[/bold blue]")
    for asset_type in AssetType:
        console.print(f"  {asset_type.name}: {asset_type.value}")

    console.print("\n[bold blue]Available Bar Sizes:[/bold blue]")
    for bar_size in BarSize:
        console.print(f"  {bar_size.name}: {bar_size.value}")

    console.print("\n[bold blue]Available Durations:[/bold blue]")
    for duration in Duration:
        console.print(f"  {duration.name}: {duration.value}")

    console.print("\n[bold blue]Available Data Types:[/bold blue]")
    for data_type in DataType:
        console.print(f"  {data_type.name}: {data_type.value}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
