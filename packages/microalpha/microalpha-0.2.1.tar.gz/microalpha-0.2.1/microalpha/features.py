
import pandas as pd
import numpy as np
from typing import Optional, Union

def _spread(df: pd.DataFrame) -> pd.Series:
    """Calculate bid-ask spread."""
    return (df["best_ask"] - df["best_bid"]).clip(lower=0)

def _midprice(df: pd.DataFrame) -> pd.Series:
    """Calculate mid-price from best bid and ask."""
    return (df["best_bid"] + df["best_ask"]) / 2.0

def compute_features(
    df: pd.DataFrame, 
    window: str = "100ms",
    *,
    include_cancel_bursts: bool = True,
    cancel_burst_threshold: int = 5
) -> pd.DataFrame:
    """
    Compute vectorized microstructure features over a time-based rolling window.
    
    This function computes the core MicroAlpha features:
    - Trade intensity (trade count per window)
    - Quote stuffing frequency (cancels per add)
    - Spread statistics (instantaneous and rolling volatility)
    - Order book imbalance
    - Mid-price and realized volatility
    - Cancel burst indicators (optional)
    
    Args:
        df: DataFrame with MicroAlpha schema (must have DatetimeIndex)
        window: Rolling window size (e.g., "50ms", "100ms", "1s", "5s")
        include_cancel_bursts: Whether to include cancel burst indicators
        cancel_burst_threshold: Minimum cancels to trigger burst flag
    
    Returns:
        DataFrame with computed features, aligned to input index
        
    Raises:
        ValueError: If input data is invalid or window format is incorrect
        
    Examples:
        # Basic usage
        features = compute_features(df, window="100ms")
        
        # Custom window with cancel burst detection
        features = compute_features(df, window="500ms", 
                                 include_cancel_bursts=True, 
                                 cancel_burst_threshold=3)
        
        # Longer-term analysis
        features = compute_features(df, window="5s")
    """
    # Input validation
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be DatetimeIndex. Use microalpha.normalize_schema() first.")
    
    if not df.index.is_monotonic_increasing:
        raise ValueError("DataFrame index must be sorted chronologically")
    
    # Validate window format
    try:
        pd.Timedelta(window)
    except ValueError:
        raise ValueError(f"Invalid window format: '{window}'. Use pandas offset format (e.g., '100ms', '1s', '5s')")
    
    # Check required columns
    required_cols = ["event_type", "side", "price", "size", "best_bid", "best_ask", "bid_size", "ask_size"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    print(f"Computing features with {window} rolling window...")
    
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
    # Add small epsilon to avoid division by zero
    out["qs_freq"] = (cancels / (adds + 1e-9)).fillna(0.0)
    
    # 3) Spread statistics
    sp = _spread(df)
    out["spread"] = sp
    out["spread_vol"] = sp.rolling(window).std()
    
    # 4) Order book imbalance
    # OBI = (bid_size - ask_size) / (bid_size + ask_size)
    # Range: [-1, 1] where negative = ask heavy, positive = bid heavy
    denom = (df["bid_size"] + df["ask_size"]).replace(0, np.nan)
    out["obi"] = ((df["bid_size"] - df["ask_size"]) / denom).fillna(0.0)
    
    # 5) Mid-price and realized volatility
    mid = _midprice(df)
    out["mid"] = mid
    
    # Realized volatility proxy (sqrt of squared log returns)
    def _realized_vol(x):
        if len(x) < 2:
            return np.nan
        log_returns = np.diff(np.log(np.maximum(x, 1e-9)))
        return np.sqrt(np.sum(log_returns**2))
    
    out["rv"] = mid.rolling(window).apply(_realized_vol, raw=False)
    
    # 6) Side-specific cancel burst indicators (optional)
    if include_cancel_bursts:
        for side, col in [("buy", "cancel_burst_buy"), ("sell", "cancel_burst_sell")]:
            mask = (df["event_type"] == "cancel") & (df["side"] == side)
            out[col] = (mask.rolling(window).sum() >= cancel_burst_threshold).astype(int)
    
    # Fill NaN values with reasonable defaults
    out = out.fillna({
        "trade_intensity": 0,
        "qs_freq": 0.0,
        "spread": 0.0,
        "spread_vol": 0.0,
        "obi": 0.0,
        "rv": 0.0
    })
    
    # Add feature metadata
    out.attrs["window"] = window
    out.attrs["features_computed"] = list(out.columns)
    out.attrs["cancel_bursts_included"] = include_cancel_bursts
    
    # Preserve essential columns needed for downstream processing
    essential_cols = ['best_bid', 'best_ask', 'symbol', 'event_type', 'side']
    for col in essential_cols:
        if col in df.columns and col not in out.columns:
            out[col] = df[col]
    
    print(f"✓ Computed {len(out.columns)} features: {list(out.columns)}")
    
    return out

def get_feature_descriptions() -> dict:
    """
    Get descriptions of all available features.
    
    Returns:
        Dictionary mapping feature names to descriptions
    """
    return {
        "trade_intensity": "Number of trades in the rolling window",
        "qs_freq": "Quote stuffing frequency: cancels per add (higher = more aggressive cancellation)",
        "spread": "Instantaneous bid-ask spread",
        "spread_vol": "Rolling volatility of the spread",
        "obi": "Order book imbalance: (bid_size - ask_size) / (bid_size + ask_size). Range: [-1, 1]",
        "mid": "Mid-price: (best_bid + best_ask) / 2",
        "rv": "Realized volatility proxy: sqrt of squared log returns in window",
        "cancel_burst_buy": "Binary indicator for buy-side cancel bursts (≥5 cancels in window)",
        "cancel_burst_sell": "Binary indicator for sell-side cancel bursts (≥5 cancels in window)"
    }

def validate_feature_parameters(window: str, include_cancel_bursts: bool, cancel_burst_threshold: int) -> None:
    """
    Validate feature computation parameters.
    
    Args:
        window: Rolling window size
        include_cancel_bursts: Whether to include cancel burst indicators
        cancel_burst_threshold: Minimum cancels to trigger burst flag
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate window
    try:
        pd.Timedelta(window)
    except ValueError:
        raise ValueError(f"Invalid window format: '{window}'. Use pandas offset format.")
    
    # Validate threshold
    if not isinstance(cancel_burst_threshold, int) or cancel_burst_threshold < 1:
        raise ValueError(f"cancel_burst_threshold must be positive integer, got {cancel_burst_threshold}")
    
    # Validate boolean
    if not isinstance(include_cancel_bursts, bool):
        raise ValueError(f"include_cancel_bursts must be boolean, got {type(include_cancel_bursts)}")
