
# MicroAlpha (starter)

A minimal, vectorized Python library for tick-level microstructure signals using rolling time windows (default 100ms).

## Features implemented
- Quote stuffing frequency (`qs_freq`): cancels per adds in window
- Spread stats: instantaneous spread and rolling volatility (`spread_vol`)
- Order book imbalance (`obi`): (bid_size - ask_size) / (bid_size + ask_size)
- Trade intensity
- Realized volatility proxy (`rv`)
- Optional cancel burst flags per side

## Quickstart

```bash
# In a virtual environment
pip install -r requirements.txt
python -m microalpha.example
```

Or use your own data:

```python
from microalpha import read_ticks, compute_features, rolling_forward_returns, join_features_and_labels

df = read_ticks("data/your_ticks.csv", ts_unit="ms")  # or "ns" / "s"
feats = compute_features(df, window="100ms")
labels = rolling_forward_returns(df, horizon="100ms")
dataset = join_features_and_labels(feats, labels)
```

## Expected CSV schema

- timestamp, symbol, event_type, side, price, size, best_bid, best_ask, bid_size, ask_size

## Notes
- Time-based rolling uses pandas offset windows (e.g. "100ms"). Ensure your index is `DatetimeIndex`.
- This starter uses synthetic data in `example.py` for a reproducible demo.


## Schema Converter
Convert any CSV to MicroAlpha schema:

```bash
python -m microalpha.convert --in data/raw.csv --out data/my_ticks.csv --symbol BTCUSDT --ts-unit ms
```
