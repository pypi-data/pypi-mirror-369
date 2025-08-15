"""
Enhanced API for MicroAlpha - Simple, user-friendly functions for common operations.
"""

from pathlib import Path
from typing import Optional, Union, Dict, Any
import pandas as pd

from .io import read_ticks, normalize_schema
from .features import compute_features
from .backtest import rolling_forward_returns, join_features_and_labels

def analyze_ticks(
    file_path: Union[str, Path, pd.DataFrame],
    *,
    window: str = "100ms",
    horizon: str = "100ms",
    ts_unit: str = "ms",
    symbol: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Analyze tick data in one line - loads, converts, and computes features.
    
    This is the main entry point for most users. It automatically:
    1. Loads your CSV file or uses provided DataFrame
    2. Converts it to MicroAlpha format if needed
    3. Computes microstructure features
    4. Generates forward return labels
    
    Args:
        file_path: Path to your CSV file or DataFrame object
        window: Rolling window for features (e.g., "100ms", "1s", "5s")
        horizon: Forward return horizon (e.g., "100ms", "1s")
        ts_unit: Timestamp unit if numeric ("ns", "ms", "s")
        symbol: Symbol name if not in your data
        **kwargs: Additional arguments passed to convert_df if conversion needed
    
    Returns:
        DataFrame with features and forward returns
        
    Examples:
        # Basic usage with standard MicroAlpha format
        features = analyze_ticks("data/ticks.csv")
        
        # Analyze DataFrame directly
        features = analyze_ticks(df, window="100ms")
        
        # Custom window and horizon
        features = analyze_ticks("data/ticks.csv", window="500ms", horizon="1s")
        
        # Auto-convert from raw data
        features = analyze_ticks("raw_data.csv", symbol="BTCUSDT", preset="binance_kline")
    """
    # Check if file_path is already a DataFrame
    if isinstance(file_path, pd.DataFrame):
        df = file_path.copy()
        print(f"✓ Using provided DataFrame with {len(df)} rows")
        # Normalize the DataFrame schema first
        df = normalize_schema(df, ts_unit=ts_unit)
        print(f"✓ Normalized DataFrame schema")
    else:
        try:
            # Try to load as standard MicroAlpha format first
            # Don't specify ts_unit initially - let pandas auto-detect
            df = read_ticks(str(file_path), ts_unit=None)
            print(f"✓ Loaded {len(df)} ticks in standard MicroAlpha format")
        except (ValueError, KeyError) as e:
            # If that fails, try to convert the data
            print(f"⚠ Converting data to MicroAlpha format...")
            df = pd.read_csv(file_path)
            
            # Add symbol if provided
            if symbol and "symbol" not in df.columns:
                df["symbol"] = symbol
                
            # Convert to MicroAlpha format using simple convert function
            df = _convert_dataframe(df, symbol=symbol, ts_unit=None, **kwargs)
            print(f"✓ Converted data with {len(df)} ticks")
    
    # Compute features and labels
    print(f"Computing features with {window} window...")
    features = compute_features(df, window=window)
    
    print(f"Generating {horizon} forward returns...")
    # rolling_forward_returns now returns DataFrame with fwd_ret column
    result = rolling_forward_returns(features, horizon=horizon)
    print(f"✓ Analysis complete! Dataset shape: {result.shape}")
    
    return result

def convert_data(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    *,
    symbol: Optional[str] = None,
    preset: Optional[str] = None,
    ts_unit: Optional[str] = None,
    **kwargs
) -> None:
    """
    Convert any CSV to MicroAlpha format with smart defaults.
    
    Args:
        input_path: Path to your input CSV
        output_path: Where to save the converted CSV
        symbol: Trading symbol (e.g., "BTCUSDT")
        preset: Data format preset ("binance_kline", "coinbase", etc.)
        ts_unit: Timestamp unit if numeric
        **kwargs: Additional conversion options
    
    Examples:
        # Convert Binance kline data
        convert_data("BTCUSDT-1s.csv", "converted.csv", 
                    symbol="BTCUSDT", preset="binance_kline")
        
        # Convert generic CSV with custom options
        convert_data("raw.csv", "converted.csv", 
                    symbol="ETHUSDT", ts_unit="ms")
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Load and convert
    df = pd.read_csv(input_path)
    converted = _convert_dataframe(df, symbol=symbol, preset=preset, ts_unit=ts_unit, **kwargs)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    converted.to_csv(output_path, index=True)
    
    print(f"✓ Converted {len(converted)} rows to {output_path}")
    print(f"Columns: {list(converted.columns)}")

def _convert_dataframe(
    df: pd.DataFrame,
    symbol: Optional[str] = None,
    preset: Optional[str] = None,
    ts_unit: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Internal function to convert DataFrame to MicroAlpha format.
    This avoids circular imports by implementing the conversion logic here.
    """
    # Simple conversion logic for common cases
    out = pd.DataFrame()
    
    # Handle timestamp
    time_cols = ["timestamp", "ts", "time", "open_time", "datetime", "date", "Date", "event_time"]
    time_col = None
    for col in time_cols:
        if col in df.columns:
            time_col = col
            break
    
    if time_col is None:
        raise ValueError("Could not find timestamp column")
    
    # Convert timestamp with better error handling
    try:
        if ts_unit:
            out["timestamp"] = pd.to_datetime(df[time_col], unit=ts_unit, errors="coerce")
        else:
            # Try to infer the format
            if df[time_col].dtype in ['int64', 'float64']:
                # Try common units
                for unit in ['ms', 's', 'ns']:
                    try:
                        out["timestamp"] = pd.to_datetime(df[time_col], unit=unit, errors="coerce")
                        if not out["timestamp"].isna().all():
                            break
                    except:
                        continue
            else:
                out["timestamp"] = pd.to_datetime(df[time_col], errors="coerce")
    except Exception as e:
        raise ValueError(f"Error converting timestamps: {e}")
    
    # Check for valid timestamps
    valid_timestamps = out["timestamp"].notna()
    if not valid_timestamps.any():
        raise ValueError("No valid timestamps found after conversion")
    
    # Handle symbol
    if symbol:
        out["symbol"] = symbol
    elif "symbol" in df.columns:
        out["symbol"] = df["symbol"]
    else:
        out["symbol"] = "UNKNOWN"
    
    # Handle event type (default to trade)
    out["event_type"] = "trade"
    
    # Handle side (default to empty)
    out["side"] = ""
    
    # Handle price
    price_cols = ["price", "p", "last_price", "close", "Close"]
    price_col = None
    for col in price_cols:
        if col in df.columns:
            price_col = col
            break
    
    if price_col:
        out["price"] = pd.to_numeric(df[price_col], errors="coerce")
    else:
        out["price"] = 0.0
    
    # Handle size/volume
    size_cols = ["size", "qty", "quantity", "volume", "vol", "Volume"]
    size_col = None
    for col in size_cols:
        if col in df.columns:
            size_col = col
            break
    
    if size_col:
        out["size"] = pd.to_numeric(df[size_col], errors="coerce")
    else:
        out["size"] = 1.0
    
    # Handle bid/ask (use price as default)
    out["best_bid"] = out["price"] - 0.01
    out["best_ask"] = out["price"] + 0.01
    
    # Handle bid/ask sizes (use size as default)
    out["bid_size"] = out["size"]
    out["ask_size"] = out["size"]
    
    # Clean up and set index
    out = out.dropna(subset=["timestamp"]).sort_values("timestamp").set_index("timestamp")
    
    # Fill NaN values with reasonable defaults
    out = out.fillna({
        "price": 0.0,
        "size": 1.0,
        "best_bid": 0.0,
        "best_ask": 0.0,
        "bid_size": 1.0,
        "ask_size": 1.0,
        "symbol": "UNKNOWN",
        "event_type": "trade",
        "side": ""
    })
    
    return out

def quick_analysis(
    file_path: Union[str, Path],
    *,
    window: str = "1s",
    horizon: str = "500ms"
) -> Dict[str, Any]:
    """
    Quick statistical analysis of your tick data.
    
    Returns a summary dictionary with key statistics and insights.
    
    Args:
        file_path: Path to your CSV file
        window: Feature computation window
        horizon: Forward return horizon
    
    Returns:
        Dictionary with analysis summary
    """
    # Load and analyze
    df = analyze_ticks(file_path, window=window, horizon=horizon)
    
    # Compute summary statistics
    summary = {
        "data_info": {
            "total_ticks": len(df),
            "time_span": f"{df.index.max() - df.index.min()}",
            "features_computed": len([c for c in df.columns if c != "fwd_ret"])
        },
        "feature_stats": {},
        "return_stats": {
            "mean_return": df["fwd_ret"].mean(),
            "volatility": df["fwd_ret"].std(),
            "sharpe_ratio": df["fwd_ret"].mean() / df["fwd_ret"].std() if df["fwd_ret"].std() > 0 else 0
        }
    }
    
    # Feature statistics (exclude fwd_ret)
    feature_cols = [c for c in df.columns if c != "fwd_ret"]
    for col in feature_cols:
        if df[col].dtype in ['float64', 'int64']:
            summary["feature_stats"][col] = {
                "mean": df[col].mean(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max()
            }
    
    return summary

def get_supported_presets() -> Dict[str, str]:
    """Get list of supported data format presets."""
    return {
        "binance_kline": "Binance 1s kline data (OHLCV)",
        "coinbase_trades": "Coinbase trade data",
        "generic": "Generic CSV with timestamp column"
    }

def validate_data_format(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate your data format and suggest conversion options.
    
    Args:
        file_path: Path to your CSV file
    
    Returns:
        Dictionary with validation results and suggestions
    """
    try:
        df = pd.read_csv(file_path)
        
        result = {
            "is_valid": False,
            "columns_found": list(df.columns),
            "missing_columns": [],
            "suggestions": [],
            "estimated_format": "unknown"
        }
        
        # Check for MicroAlpha format
        required_cols = ["timestamp", "symbol", "event_type", "side", "price", 
                        "size", "best_bid", "best_ask", "bid_size", "ask_size"]
        
        missing = [col for col in required_cols if col not in df.columns]
        result["missing_columns"] = missing
        
        if not missing:
            result["is_valid"] = True
            result["estimated_format"] = "microalpha_standard"
            result["suggestions"].append("Data is already in MicroAlpha format!")
        else:
            # Try to identify format
            if "open" in df.columns and "close" in df.columns and "volume" in df.columns:
                result["estimated_format"] = "ohlcv_kline"
                result["suggestions"].append("Data appears to be OHLCV format - use preset='binance_kline'")
            
            if "timestamp" in df.columns or "time" in df.columns:
                result["suggestions"].append("Timestamp column found - may need ts_unit specification")
            
            result["suggestions"].append(f"Use convert_data() with appropriate preset")
        
        return result
        
    except Exception as e:
        return {
            "is_valid": False,
            "error": str(e),
            "suggestions": ["Check file path and format", "Ensure file is valid CSV"]
        } 