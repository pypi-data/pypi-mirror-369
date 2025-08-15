
import pandas as pd
import numpy as np

# Expected normalized schema:
# ["timestamp", "symbol", "event_type", "side", "price", "size", "best_bid", "best_ask", "bid_size", "ask_size"]
# timestamp must be ns or ms; function will convert to pandas datetime and set index.

def read_ticks(path: str, ts_unit: str = "ns") -> pd.DataFrame:
    """
    Read and normalize tick data from CSV file.
    
    Args:
        path: Path to CSV file
        ts_unit: Timestamp unit ("ns", "ms", "s", or None for auto-detection)
    
    Returns:
        Normalized DataFrame with DatetimeIndex
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If data format is invalid
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}. Please check the file path.")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    return normalize_schema(df, ts_unit=ts_unit)

def normalize_schema(df: pd.DataFrame, ts_unit: str = "ns") -> pd.DataFrame:
    """
    Normalize DataFrame to MicroAlpha schema.
    
    Args:
        df: Input DataFrame
        ts_unit: Timestamp unit ("ns", "ms", "s", or None for auto-detection)
    
    Returns:
        Normalized DataFrame with DatetimeIndex
        
    Raises:
        ValueError: If required columns are missing or data is invalid
    """
    required = ["timestamp","symbol","event_type","side","price","size","best_bid","best_ask","bid_size","ask_size"]
    
    # Check for missing columns
    missing = [c for c in required if c not in df.columns]
    if missing:
        # Provide helpful suggestions
        suggestions = []
        if "time" in df.columns or "ts" in df.columns:
            suggestions.append("Found 'time' or 'ts' column - try renaming to 'timestamp'")
        if "bid" in df.columns and "ask" in df.columns:
            suggestions.append("Found bid/ask columns - may need to rename to 'best_bid'/'best_ask'")
        if "qty" in df.columns or "quantity" in df.columns:
            suggestions.append("Found quantity column - try renaming to 'size'")
        
        error_msg = f"Missing required columns: {missing}\n"
        if suggestions:
            error_msg += "Suggestions:\n" + "\n".join(f"  - {s}" for s in suggestions)
        error_msg += f"\n\nUse microalpha.convert_data() to convert your data format."
        
        raise ValueError(error_msg)
    
    # Validate timestamp unit
    if ts_unit is not None and ts_unit not in {"ns","ms","s"}:
        raise ValueError(f"ts_unit must be 'ns', 'ms', 's', or None, got '{ts_unit}'")
    
    df = df.copy()
    
    # Convert timestamp with better error handling
    try:
        if ts_unit is None:
            # Auto-detect timestamp format
            if df["timestamp"].dtype in ['int64', 'float64']:
                # Try to infer the unit
                sample_ts = df["timestamp"].dropna().iloc[0] if not df["timestamp"].dropna().empty else 0
                if sample_ts > 1e17:
                    ts_unit = "ns"
                elif sample_ts > 1e11:
                    ts_unit = "ms"
                elif sample_ts > 1e8:
                    ts_unit = "s"
                else:
                    # Assume it's already in datetime format
                    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                    ts_unit = None
            
            if ts_unit:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit=ts_unit, errors="coerce")
        elif ts_unit == "ns":
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        elif ts_unit == "ms":
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        else:  # ts_unit == "s"
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        
        # Ensure we have a proper DatetimeIndex
        if not isinstance(df["timestamp"].dtype, pd.DatetimeTZDtype) and df["timestamp"].dtype != 'datetime64[ns]':
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            
    except Exception as e:
        raise ValueError(f"Error converting timestamps with unit '{ts_unit}': {e}\n"
                       f"Try a different ts_unit or check your timestamp format.")
    
    # Check for invalid timestamps
    invalid_ts = df["timestamp"].isna().sum()
    if invalid_ts > 0:
        print(f"Warning: {invalid_ts} invalid timestamps found and will be dropped")
        df = df.dropna(subset=["timestamp"])
    
    if len(df) == 0:
        raise ValueError("No valid timestamps found after conversion")
    
    # Sort and set index
    df = df.sort_values("timestamp").set_index("timestamp")
    
    # Ensure numeric columns are numeric with better error handling
    numeric_cols = ["price","size","best_bid","best_ask","bid_size","ask_size"]
    for col in numeric_cols:
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # Fill NaN with reasonable defaults
            if col == "size":
                df[col] = df[col].fillna(1.0)  # Default size of 1
            elif col in ["bid_size", "ask_size"]:
                df[col] = df[col].fillna(df["size"])  # Use trade size as default
            else:
                df[col] = df[col].fillna(0.0)
        except Exception as e:
            raise ValueError(f"Error converting column '{col}' to numeric: {e}")
    
    # Clean categorical columns
    df["side"] = df["side"].fillna("").str.lower()
    df["event_type"] = df["event_type"].fillna("").str.lower()
    df["symbol"] = df["symbol"].fillna("UNKNOWN").astype(str)
    
    # Validate event types
    valid_events = {"trade", "add", "cancel", ""}
    invalid_events = set(df["event_type"].unique()) - valid_events
    if invalid_events:
        print(f"Warning: Found invalid event types: {invalid_events}")
        # Map common variations
        event_mapping = {
            "t": "trade", "fill": "trade", "execution": "trade",
            "new": "add", "insert": "add", "update": "add",
            "u": "add",
            "delete": "cancel", "remove": "cancel", "cxl": "cancel",
        }
        df["event_type"] = df["event_type"].map(event_mapping).fillna(df["event_type"])
    
    # Validate sides
    valid_sides = {"buy", "sell", ""}
    invalid_sides = set(df["side"].unique()) - valid_sides
    if invalid_sides:
        print(f"Warning: Found invalid sides: {invalid_sides}")
        # Map common variations
        side_mapping = {
            "b": "buy", "bid": "buy",
            "s": "sell", "ask": "sell", "a": "sell"
        }
        df["side"] = df["side"].map(side_mapping).fillna(df["side"])
    
    # Final validation
    if len(df) == 0:
        raise ValueError("No valid data remaining after normalization")
    
    print(f"✓ Successfully normalized {len(df)} ticks")
    print(f"  Time range: {df.index.min()} to {df.index.max()}")
    print(f"  Symbols: {df['symbol'].unique()}")
    print(f"  Event types: {[e for e in df['event_type'].unique() if e]}")
    
    return df
