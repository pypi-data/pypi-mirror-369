
import pandas as pd

# Expected normalized schema:
# ["timestamp", "symbol", "event_type", "side", "price", "size", "best_bid", "best_ask", "bid_size", "ask_size"]
# timestamp must be ns or ms; function will convert to pandas datetime and set index.

def read_ticks(path: str, ts_unit: str = "ns") -> pd.DataFrame:
    df = pd.read_csv(path)
    return normalize_schema(df, ts_unit=ts_unit)

def normalize_schema(df: pd.DataFrame, ts_unit: str = "ns") -> pd.DataFrame:
    required = ["timestamp","symbol","event_type","side","price","size","best_bid","best_ask","bid_size","ask_size"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    # Convert timestamp
    if ts_unit not in {"ns","ms","s"}:
        raise ValueError("ts_unit must be 'ns', 'ms', or 's'")
    df = df.copy()
    if ts_unit == "ns":
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    elif ts_unit == "ms":
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.sort_values("timestamp").set_index("timestamp")
    # Ensure numeric columns are numeric
    for c in ["price","size","best_bid","best_ask","bid_size","ask_size"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    # Clean side, event_type
    df["side"] = df["side"].fillna("").str.lower()
    df["event_type"] = df["event_type"].fillna("").str.lower()
    return df
