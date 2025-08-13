
import pandas as pd
import numpy as np

def rolling_forward_returns(df: pd.DataFrame, horizon: str = "100ms") -> pd.Series:
    """Compute forward log-return of midprice over given horizon."""
    if "best_bid" not in df.columns or "best_ask" not in df.columns:
        raise ValueError("df must include best_bid and best_ask")
    mid = (df["best_bid"] + df["best_ask"]) / 2.0
    fut = mid.shift(freq=horizon)
    ret = (np.log(fut.replace(0, np.nan)) - np.log(mid.replace(0, np.nan)))
    return ret

def join_features_and_labels(features: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    out = features.copy()
    out["fwd_ret"] = labels
    return out.dropna()
