"""
Daily aggregation module for client transaction data.
Aggregates transactions by day and term_owner_name with complete date ranges.
"""

import pandas as pd


def aggregate_by_day(
    df_historical: pd.DataFrame,
    date_column: str = "datetime_b",
    client_column: str = "term_owner_name",
    amount_columns: list[str] | None = None,
    fill_missing_dates: bool = True,
) -> pd.DataFrame:
    """
    Aggregate transaction data by day and client, optionally filling missing dates.

    Args:
        df_historical: DataFrame with transaction data
        date_column: Name of the date column (default: "datetime_b")
        client_column: Name of the client identifier column (default: "term_owner_name")
        amount_columns: List of amount columns to aggregate (default: ["amt_1", "amt_2", "transaction_count"])
        fill_missing_dates: Whether to fill missing dates with zeros (default: True)

    Returns:
        DataFrame aggregated by day and client
    """
    # Convert date column to datetime if not already
    df = df_historical.copy()
    df[date_column] = pd.to_datetime(df[date_column])

    # Set default amount columns if not provided
    if amount_columns is None:
        amount_columns = ["amt_1", "amt_2", "transaction_count"]

    # Filter to only include columns that exist in the dataframe
    existing_amount_columns = [col for col in amount_columns if col in df.columns]

    if not existing_amount_columns:
        raise ValueError(f"None of the specified amount columns {amount_columns} exist in the dataframe")

    # Aggregate by day and client
    df_daily_agg = (
        df.groupby([date_column, client_column]).agg({col: "sum" for col in existing_amount_columns}).reset_index()
    )

    if not fill_missing_dates:
        return df_daily_agg

    # Create complete date ranges for each client
    # Get min and max dates for each client
    date_ranges = df.groupby(client_column)[date_column].agg(["min", "max"]).reset_index()

    # Create complete date range for each client
    complete_dates = []
    for _, row in date_ranges.iterrows():
        client = row[client_column]
        start_date = row["min"]
        end_date = row["max"]

        # Create daily range
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")

        # Create DataFrame for this client's dates
        client_dates = pd.DataFrame({date_column: date_range, client_column: client})
        complete_dates.append(client_dates)

    # Combine all date ranges
    if complete_dates:
        df_complete = pd.concat(complete_dates, ignore_index=True)

        # Merge with aggregated data to fill missing dates with zeros
        df_final = pd.merge(df_complete, df_daily_agg, on=[date_column, client_column], how="left").fillna(0)

        # Sort by client and date
        df_final = df_final.sort_values([client_column, date_column]).reset_index(drop=True)

        return df_final
    else:
        return df_daily_agg


# Example usage (when run directly)
if __name__ == "__main__":
    # This would be used when testing the module directly
    print("agg_by_day module loaded successfully!")
    print("Use aggregate_by_day(df_historical) to aggregate your data by day and client.")
