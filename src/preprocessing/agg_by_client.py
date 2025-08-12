"""
Client aggregation module for churn prediction.
Refactored to use configuration files and modular functions.
"""

from typing import Any

import pandas as pd
import yaml


def load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path) as file:
        return yaml.safe_load(file)


def load_and_preprocess_data(data_path: str, config: dict[str, Any]) -> pd.DataFrame:
    """Load and preprocess the raw data."""
    print(f"Loading data from {data_path}...")
    df = pd.read_parquet(data_path)

    df["retl_sic_cde.descripcion"] = df["retl_sic_cde.descripcion"].fillna("Unknown")
    df["retl_sic_cde.familia"] = df["retl_sic_cde.familia"].fillna("Others")

    if "retl_sic_cde.mcc" in df.columns:
        mode_mcc = df["retl_sic_cde.mcc"].mode()[0]
        df["retl_sic_cde.mcc"] = df["retl_sic_cde.mcc"].fillna(mode_mcc)

    scale_factor = config["features"]["transformations"]["amt_scale_factor"]
    df["amt_1"] = df["amt_1"] / scale_factor
    df["amt_2"] = df["amt_2"] / scale_factor

    df = df.sort_values(by="datetime_b")

    columns_to_drop = config["features"]["columns_to_drop"]
    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing_columns_to_drop)

    df["datetime_b"] = pd.to_datetime(df["datetime_b"])
    max_date = config["data_split"].get("max_data_date")
    if max_date:
        df = df[df["datetime_b"] <= max_date]

    df["transaction_count"] = 1

    print(f"Preprocessed data shape: {df.shape}")
    return df


def split_data_by_periods(df: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split data into historical, target, and validation periods.

    Timeline:
    - Historical: up to cutoff_date (used for training features)
    - Target: 2 weeks after cutoff (used for training labels)
    - Validation: 4 weeks after cutoff (used for validation labels)
    """
    cutoff_date = pd.to_datetime(config["data_split"]["cutoff_date"])

    # Automatically calculate target period: next 2 weeks after cutoff
    target_start = cutoff_date + pd.Timedelta(days=1)
    target_end = target_start + pd.Timedelta(days=13)  # 14 days total (2 weeks)

    # Automatically calculate validation period: next 2 weeks after target (4 weeks after cutoff)
    val_start = target_end + pd.Timedelta(days=1)
    val_end = val_start + pd.Timedelta(days=13)  # 14 days total (2 weeks)

    # Historical data (features)
    df_historical = df[df["datetime_b"] <= cutoff_date].copy()

    # Target period (for labels)
    df_target = df[(df["datetime_b"] >= target_start) & (df["datetime_b"] <= target_end)].copy()

    # Validation period
    df_validation = df[(df["datetime_b"] >= val_start) & (df["datetime_b"] <= val_end)].copy()

    print("Date periods:")
    print(f"  Historical: up to {cutoff_date.date()}")
    print(f"  Target: {target_start.date()} to {target_end.date()}")
    print(f"  Validation: {val_start.date()} to {val_end.date()}")
    print()
    print("Data distribution:")
    print(f"  Historical data: {df_historical.shape[0]} transactions")
    print(f"  Target period data: {df_target.shape[0]} transactions")
    print(f"  Validation period data: {df_validation.shape[0]} transactions")

    return df_historical, df_target, df_validation


def aggregate_client_features(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Aggregate features by client (term_owner_name)."""
    aggregations = config["features"]["aggregations"]

    df_agg = df.groupby("term_owner_name").agg(aggregations).reset_index()

    # Calculate derived features
    df_agg["average_ticket"] = df_agg["amt_1"] / df_agg["transaction_count"]

    # Handle division by zero
    df_agg["average_ticket"] = df_agg["average_ticket"].fillna(0)

    print(f"Aggregated features for {df_agg.shape[0]} unique clients")
    return df_agg


def create_churn_labels(df_features: pd.DataFrame, df_target: pd.DataFrame) -> pd.DataFrame:
    """Create churn labels based on activity in target period."""
    # Get clients active in target period
    active_clients = set(df_target["term_owner_name"].unique())

    # Create churn label: 1 if client was NOT active in target period
    df_features = df_features.copy()
    df_features["future_churn"] = ~df_features["term_owner_name"].isin(active_clients)
    df_features["future_churn"] = df_features["future_churn"].astype(int)

    churn_rate = df_features["future_churn"].mean()
    print(f"Churn rate: {churn_rate:.2%} ({df_features['future_churn'].sum()} out of {len(df_features)} clients)")

    return df_features


def create_validation_merchants(df_validation: pd.DataFrame) -> list[str]:
    """Create validation dataset using historical data up to cutoff date and validation period for labels."""
    unique_merchants = df_validation["term_owner_name"].unique()
    return unique_merchants.tolist()


def run_preprocessing_pipeline():
    """Execute the preprocessing pipeline for client aggregation and churn prediction."""
    # Load configuration
    config_path = "/workspaces/linux_env/configs/data_split.yaml"
    config = load_config(config_path)

    # Load and preprocess data
    data_path = "/workspaces/linux_env/data/pltf.parquet"
    df_processed = load_and_preprocess_data(data_path, config)

    # Split data by periods
    df_historical, df_target, df_validation = split_data_by_periods(df_processed, config)

    # Create training dataset (features from historical + labels from target)
    print("\n=== Creating Training Dataset ===")
    df_train_features = aggregate_client_features(df_historical, config)
    df_train = create_churn_labels(df_train_features, df_target)

    print("\n=== Creating Validation Dataset ===")
    val_merchants = create_validation_merchants(df_validation)

    # Display summary
    print("\n=== Dataset Summary ===")
    print(f"Training dataset: {df_train.shape}")
    print(f"Training churn rate: {df_train['future_churn'].mean():.2%}")

    # Display sample data
    print("\n=== Training Dataset Sample ===")
    print(df_train.head())

    return {
        "df_historical": df_historical,
        "df_target": df_target,
        "df_validation": df_validation,
        "df_train": df_train,
        "val_merchants": val_merchants,
        "config": config,
    }


if __name__ == "__main__":
    # Check if PyYAML is available
    try:
        import yaml
    except ImportError:
        print("PyYAML is required. Please install it with: pip install pyyaml")
        exit(1)

    results = run_preprocessing_pipeline()
