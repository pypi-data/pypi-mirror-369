
import pandas as pd
import numpy as np

def _spread(df: pd.DataFrame) -> pd.Series:
    return (df["best_ask"] - df["best_bid"]).clip(lower=0)

def _midprice(df: pd.DataFrame) -> pd.Series:
    return (df["best_ask"] + df["best_bid"]) / 2.0

def compute_features(df: pd.DataFrame, window: str = "100ms") -> pd.DataFrame:
    """
    Vectorized microstructure features over a time-based rolling window.
    df must be normalized and indexed by timestamp (see io.normalize_schema).
    window: pandas offset alias like '50ms', '100ms', '1s'.
    Returns a DataFrame aligned to df's index with feature columns.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("df index must be DatetimeIndex")

    out = pd.DataFrame(index=df.index)

    # 1) Trade intensity (count of trades per window)
    is_trade = (df["event_type"] == "trade")
    out["trade_intensity"] = is_trade.rolling(window).sum()

    # 2) Cancel/Add intensity (proxy for quote stuffing)
    is_add = (df["event_type"] == "add")
    is_cancel = (df["event_type"] == "cancel")
    adds = is_add.rolling(window).sum()
    cancels = is_cancel.rolling(window).sum()
    # Quote stuffing frequency: cancels per add within the window
    # Add 1e-9 to avoid division by zero.
    out["qs_freq"] = (cancels / (adds + 1e-9)).fillna(0.0)

    # 3) Spread stats
    sp = _spread(df)
    out["spread"] = sp
    out["spread_vol"] = sp.rolling(window).std()

    # 4) Order book imbalance
    denom = (df["bid_size"] + df["ask_size"]).replace(0, np.nan)
    out["obi"] = ((df["bid_size"] - df["ask_size"]) / denom).fillna(0.0)

    # 5) Short-horizon midprice return (future label sometimes)
    mid = _midprice(df)
    out["mid"] = mid
    # Lagged and lead returns can be used outside as labels; keep level features here
    # Provide a near-term realized volatility proxy too
    out["rv"] = mid.rolling(window).apply(lambda x: np.sqrt(np.sum(np.diff(np.log(np.maximum(x,1e-9)))**2)), raw=False)

    # 6) Side-specific cancel burst indicators (optional binary)
    for side, col in [("buy","cancel_burst_buy"), ("sell","cancel_burst_sell")]:
        mask = (df["event_type"] == "cancel") & (df["side"] == side)
        out[col] = (mask.rolling(window).sum() >= 5).astype(int)  # threshold tweakable

    return out
