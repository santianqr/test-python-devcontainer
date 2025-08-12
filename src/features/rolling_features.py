"""
Rolling features module for client transaction data.
Creates rolling window features for time series analysis.
"""

from typing import Any

import pandas as pd


def create_rolling_features(
    df_daily_agg: pd.DataFrame,
    config: dict[str, Any],
    client_column: str = "term_owner_name",
    date_column: str = "datetime_b",
) -> pd.DataFrame:
    """
    Create rolling window features for time series analysis.

    Args:
        df_daily_agg: DataFrame from aggregate_by_day function
        config: Configuration dictionary with rolling feature parameters
        client_column: Name of the client identifier column
        date_column: Name of the date column

    Returns:
        DataFrame with rolling features added
    """
    # Sort by client and date for proper rolling calculations
    df = df_daily_agg.sort_values(by=[client_column, date_column]).copy()

    # Get rolling feature configuration
    rolling_config = config.get("rolling_features", {})

    if not rolling_config:
        print("Warning: No rolling_features configuration found in config")
        return df

    # Get window sizes configuration
    windows = rolling_config.get("windows", {})

    if not windows:
        print("Warning: No windows configuration found. Using default windows.")
        windows = {"short_term": 14, "medium_term": 28, "long_term": 56}

    # Validate configuration
    print("=== Rolling Features Configuration ===")
    print(f"Windows: {windows}")
    print(f"Amount features: {list(rolling_config.get('amount_features', {}).keys())}")
    print(f"Transaction features: {list(rolling_config.get('transaction_features', {}).keys())}")

    # Show what features will be created
    print("\n=== Features to be created ===")
    amount_features = rolling_config.get("amount_features", {})
    for feature_name, feature_config in amount_features.items():
        base_column = feature_config.get("base_column", "amt_1")
        window_key = feature_config.get("window", "medium_term")
        window_days = windows.get(window_key, 28)
        operation = feature_config.get("operation", "sum")
        print(f"  {feature_name}: {operation} of {base_column} over {window_days} days ({window_key})")

    txn_features = rolling_config.get("transaction_features", {})
    if txn_features.get("drop_vs_max", False):
        print("  txn_drop_vs_max: transaction count / max transaction count")
    if txn_features.get("no_txn_today", False):
        print("  no_txn_today: flag for days with no transactions")

    for feature_name, feature_config in txn_features.items():
        if feature_name.startswith("days_without_txn"):
            window_key = feature_config.get("window", "long_term")
            window_days = windows.get(window_key, 56)
            print(f"  {feature_name}: sum of no_txn_today over {window_days} days ({window_key})")
    print()

    # Amount rolling features
    amount_features = rolling_config.get("amount_features", {})
    if not amount_features:
        print("Warning: No amount_features configured")

    for feature_name, feature_config in amount_features.items():
        if not isinstance(feature_config, dict):
            print(f"Warning: Invalid configuration for {feature_name}, skipping")
            continue

        base_column = feature_config.get("base_column", "amt_1")
        window_key = feature_config.get("window", "medium_term")
        window_days = windows.get(window_key, 28)  # Default to 28 days if window not found
        operation = feature_config.get("operation", "sum")

        if base_column in df.columns:
            if operation == "std":
                df[feature_name] = (
                    df.groupby(client_column)[base_column]
                    .rolling(window=window_days, min_periods=1)
                    .std()
                    .reset_index(level=0, drop=True)
                )
                print(f"Created feature: {feature_name} with window {window_days} days")
            elif operation == "sum":
                df[feature_name] = (
                    df.groupby(client_column)[base_column]
                    .rolling(window=window_days, min_periods=1)
                    .sum()
                    .reset_index(level=0, drop=True)
                )
                print(f"Created feature: {feature_name} with window {window_days} days")

    # Transaction count features
    txn_features = rolling_config.get("transaction_features", {})
    if not txn_features:
        print("Warning: No transaction_features configured")

    # Transaction drop vs max
    if txn_features.get("drop_vs_max", True):
        txn_max = df.groupby(client_column)["transaction_count"].transform("max")
        df["txn_drop_vs_max"] = df["transaction_count"] / txn_max
        print("Created feature: txn_drop_vs_max")

    # No transaction today flag
    if txn_features.get("no_txn_today", True):
        df["no_txn_today"] = (df["transaction_count"] == 0).astype(int)
        print("Created feature: no_txn_today")

    # Days without transactions rolling window
    for feature_name, feature_config in txn_features.items():
        if feature_name.startswith("days_without_txn"):
            window_key = feature_config.get("window", "long_term")
            window_days = windows.get(window_key, 56)  # Default to 56 days if window not found

            # Make sure no_txn_today column exists
            if "no_txn_today" in df.columns:
                df[feature_name] = (
                    df.groupby(client_column)["no_txn_today"]
                    .rolling(window=window_days, min_periods=1)
                    .sum()
                    .reset_index(level=0, drop=True)
                )
                print(f"Created feature: {feature_name} with window {window_days} days")

    # Final check - ensure we have at least some features
    feature_columns = [
        col
        for col in df.columns
        if col not in ["datetime_b", "term_owner_name", "amt_1", "amt_2", "transaction_count"]
    ]
    if not feature_columns:
        print("Warning: No rolling features were created. Check your configuration.")
    else:
        print(f"Successfully created {len(feature_columns)} rolling features: {feature_columns}")

    return df


def extract_last_features(
    df_with_features: pd.DataFrame,
    config: dict[str, Any],
    client_column: str = "term_owner_name",
    date_column: str = "datetime_b",
) -> pd.DataFrame:
    """
    Extract the last (most recent) features for each client.

    Args:
        df_with_features: DataFrame with rolling features from create_rolling_features
        config: Configuration dictionary
        client_column: Name of the client identifier column
        date_column: Name of the date column

    Returns:
        DataFrame with last features for each client
    """
    rolling_config = config.get("rolling_features", {})

    # Get list of feature columns to extract
    feature_columns = rolling_config.get("extract_features", [])

    if not feature_columns:
        # Auto-generate feature names from configuration to avoid mismatches
        rolling_config = config.get("rolling_features", {})

        # Get amount features
        amount_features = rolling_config.get("amount_features", {})
        amount_feature_names = list(amount_features.keys())

        # Get transaction features
        txn_features = rolling_config.get("transaction_features", {})
        txn_feature_names = []

        if txn_features.get("drop_vs_max", False):
            txn_feature_names.append("txn_drop_vs_max")

        # Add days without transaction features
        for feature_name in txn_features.keys():
            if feature_name.startswith("days_without_txn"):
                txn_feature_names.append(feature_name)

        feature_columns = amount_feature_names + txn_feature_names

        print(f"Auto-generated feature columns: {feature_columns}")

    # Filter to only include columns that exist
    existing_features = [col for col in feature_columns if col in df_with_features.columns]
    missing_features = [col for col in feature_columns if col not in df_with_features.columns]

    if missing_features:
        print(f"Warning: The following features were not found in the dataframe: {missing_features}")
        print(
            f"Available features: {[col for col in df_with_features.columns if col not in ['datetime_b', 'term_owner_name', 'amt_1', 'amt_2', 'transaction_count']]}"
        )

    if not existing_features:
        print("Warning: No specified features found in dataframe")
        return pd.DataFrame()

    # Get last features for each client
    last_features = (
        df_with_features.sort_values(date_column).groupby(client_column).last()[existing_features].reset_index()
    )

    return last_features


def create_rolling_features_pipeline(
    df_daily_agg: pd.DataFrame,
    config: dict[str, Any],
    client_column: str = "term_owner_name",
    date_column: str = "datetime_b",
) -> dict[str, pd.DataFrame]:
    """
    Complete pipeline to create rolling features and extract last values.

    Args:
        df_daily_agg: DataFrame from aggregate_by_day function
        config: Configuration dictionary
        client_column: Name of the client identifier column
        date_column: Name of the date column

    Returns:
        Dictionary containing:
        - 'df_with_features': DataFrame with all rolling features
        - 'last_features': DataFrame with last features for each client
    """
    # Create rolling features
    df_with_features = create_rolling_features(df_daily_agg, config, client_column, date_column)

    # Auto-generate extract_features if missing or if there are mismatches
    rolling_config = config.get("rolling_features", {})

    # Always get amount and transaction features (needed for mismatch checking)
    amount_features = rolling_config.get("amount_features", {})
    txn_features = rolling_config.get("transaction_features", {})

    if "extract_features" not in rolling_config or not rolling_config["extract_features"]:
        print("Auto-generating extract_features list...")

        amount_feature_names = list(amount_features.keys())
        txn_feature_names = []

        if txn_features.get("drop_vs_max", False):
            txn_feature_names.append("txn_drop_vs_max")

        # Add days without transaction features
        for feature_name in txn_features.keys():
            if feature_name.startswith("days_without_txn"):
                txn_feature_names.append(feature_name)

        rolling_config["extract_features"] = amount_feature_names + txn_feature_names
        print(f"Auto-generated extract_features: {rolling_config['extract_features']}")

    # Check for mismatches between extract_features and actual features
    actual_features = []
    if amount_features:
        actual_features.extend(list(amount_features.keys()))
    if txn_features.get("drop_vs_max", False):
        actual_features.append("txn_drop_vs_max")
    for feature_name in txn_features.keys():
        if feature_name.startswith("days_without_txn"):
            actual_features.append(feature_name)

    extract_features = rolling_config.get("extract_features", [])
    mismatched_features = [f for f in extract_features if f not in actual_features]

    if mismatched_features:
        print(f"Warning: extract_features contains features that don't exist: {mismatched_features}")
        print(f"Updating extract_features to match actual features: {actual_features}")
        rolling_config["extract_features"] = actual_features

    # Final validation
    if not actual_features:
        print("Warning: No features will be created. Check your configuration.")
        print(f"Amount features: {amount_features}")
        print(f"Transaction features: {txn_features}")
    else:
        print(f"Final features to extract: {rolling_config.get('extract_features', [])}")

    # Extract last features
    last_features = extract_last_features(df_with_features, config, client_column, date_column)

    return {"df_with_features": df_with_features, "last_features": last_features}


# Example usage (when run directly)
if __name__ == "__main__":
    print("rolling_features module loaded successfully!")
    print("Use create_rolling_features(df_daily_agg, config) to create rolling features.")
    print("Use create_rolling_features_pipeline(df_daily_agg, config) for complete pipeline.")
