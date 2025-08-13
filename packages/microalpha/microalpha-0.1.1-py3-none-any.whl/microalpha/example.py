
"""
Example usage with synthetic ticks.
Run: python -m microalpha.example
"""
import pandas as pd
import numpy as np
from .io import normalize_schema
from .features import compute_features
from .backtest import rolling_forward_returns, join_features_and_labels

def _make_synth(n=20000, symbol="ABC"):
    rng = np.random.default_rng(42)
    # 1ms spacing baseline
    t0 = np.datetime64("2025-01-02T09:30:00.000000000")
    ts = t0 + np.arange(n).astype("timedelta64[ms]")
    best_bid = 100 + np.cumsum(rng.normal(0, 0.001, size=n))
    best_ask = best_bid + rng.uniform(0.01, 0.05, size=n)
    bid_size = rng.integers(100, 1000, size=n)
    ask_size = rng.integers(100, 1000, size=n)

    # Random events
    events = rng.choice(["trade","add","cancel"], size=n, p=[0.2,0.5,0.3])
    sides = rng.choice(["buy","sell",""], size=n, p=[0.45,0.45,0.1])
    # Inject a cancel burst region to simulate quote stuffing
    burst_idx = slice(5000,5200)
    events[burst_idx] = "cancel"
    sides[burst_idx] = "sell"

    price = best_bid + (best_ask - best_bid) * rng.random(size=n)
    size = rng.integers(1, 100, size=n)

    df = pd.DataFrame({
        "timestamp": ts,
        "symbol": symbol,
        "event_type": events,
        "side": sides,
        "price": price,
        "size": size,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "bid_size": bid_size,
        "ask_size": ask_size,
    })
    return df

def main():
    raw = _make_synth()
    df = normalize_schema(raw, ts_unit="ns")
    feats = compute_features(df, window="100ms")
    labels = rolling_forward_returns(df, horizon="100ms")
    ds = join_features_and_labels(feats, labels)
    print(ds.head(10))
    print("Dataset shape:", ds.shape)
    # Simple threshold "strategy" example
    signal = (ds["qs_freq"] > 1.0) & (ds["obi"] < -0.2)
    pnl = signal.shift(1).fillna(False) * ds["fwd_ret"]
    print("Toy strategy mean fwd_ret:", pnl.mean())

if __name__ == "__main__":
    main()
