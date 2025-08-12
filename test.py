import yaml

from src.features.rolling_features import create_rolling_features_pipeline
from src.preprocessing.agg_by_client import run_preprocessing_pipeline
from src.preprocessing.agg_by_day import aggregate_by_day

# Run the preprocessing pipeline
results = run_preprocessing_pipeline()

# Extract results
df_train = results["df_train"]
val_merchants = results["val_merchants"]
df_historical = results["df_historical"]
# df_target = results["df_target"]
# df_validation = results["df_validation"]
config = results["config"]

# Aggregate historical data by day and client
print("\n=== Aggregating Data by Day and Client ===")
df_daily_agg = aggregate_by_day(df_historical)

print(f"Daily aggregated data shape: {df_daily_agg.shape}")
print(f"Date range: {df_daily_agg['datetime_b'].min()} to {df_daily_agg['datetime_b'].max()}")
print(f"Number of unique clients: {df_daily_agg['term_owner_name'].nunique()}")

# Show sample of daily aggregated data
print("\n=== Sample Daily Aggregated Data ===")
print(df_daily_agg.head(10))

# Load features configuration directly from file
print("\n=== Loading Features Configuration ===")
with open("configs/features.yaml") as file:
    features_config = yaml.safe_load(file)
print("Features configuration loaded successfully!")

# Create rolling features
print("\n=== Creating Rolling Features ===")
rolling_results = create_rolling_features_pipeline(df_daily_agg, features_config)

df_with_features = rolling_results["df_with_features"]
last_features = rolling_results["last_features"]

print(f"DataFrame with features shape: {df_with_features.shape}")
print(f"Last features shape: {last_features.shape}")

# Show sample of features
print("\n=== Sample Rolling Features ===")
feature_columns = [
    col
    for col in df_with_features.columns
    if col not in ["datetime_b", "term_owner_name", "amt_1", "amt_2", "transaction_count"]
]
print(f"Number of rolling features created: {len(feature_columns)}")
print("Feature columns:", feature_columns[:10])  # Show first 10 features

# Show sample of last features for each client
print("\n=== Sample Last Features (Final Dataset) ===")
print(last_features.head())

# Show feature statistics
print("\n=== Feature Statistics ===")
print(f"Features available: {len(feature_columns)}")
print(f"Clients with features: {len(last_features)}")

# You can now use these DataFrames for further analysis:
# - df_with_features: Complete time series with rolling features
# - last_features: Final features for each client (ready for ML)
# - df_daily_agg: Original daily aggregated data
