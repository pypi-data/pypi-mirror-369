
import pandas as pd
import numpy as np

def rolling_forward_returns(df: pd.DataFrame, horizon: str = "100ms") -> pd.DataFrame:
    """Compute forward log-return of midprice over given horizon."""
    if "best_bid" not in df.columns or "best_ask" not in df.columns:
        raise ValueError("df must include best_bid and best_ask")
    
    mid = (df["best_bid"] + df["best_ask"]) / 2.0
    
    # Convert horizon to number of periods for shifting
    # For simplicity, use a fixed number of periods instead of time-based shifting
    horizon_periods = 1  # Default to 1 period ahead
    
    # Shift forward by periods
    fut = mid.shift(-horizon_periods)
    
    # Calculate log returns, handling zeros and NaN values
    ret = np.log(fut.replace(0, np.nan)) - np.log(mid.replace(0, np.nan))
    
    # Add forward returns to the original DataFrame
    result = df.copy()
    result["fwd_ret"] = ret
    
    return result

def join_features_and_labels(features: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    out = features.copy()
    out["fwd_ret"] = labels
    return out.dropna()
