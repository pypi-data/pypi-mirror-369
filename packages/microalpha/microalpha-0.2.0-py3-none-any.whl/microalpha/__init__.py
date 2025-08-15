"""
MicroAlpha - A Python library for analyzing ultra-high-frequency tick data and discovering micro-alpha trading signals.

Quick Start:
    from microalpha import analyze_ticks, convert_data
    
    # Analyze tick data in one line
    features = analyze_ticks("data/ticks.csv")
    
    # Convert any CSV to MicroAlpha format
    convert_data("raw_data.csv", "converted.csv", symbol="BTCUSDT")
"""

__version__ = "0.1.2"

# Core functionality
from .io import read_ticks, normalize_schema
from .features import compute_features, get_feature_descriptions
from .backtest import rolling_forward_returns, join_features_and_labels

# Simplified API
from .simple import Buffer

# Enhanced API functions
from .enhanced import analyze_ticks, convert_data, quick_analysis, get_supported_presets, validate_data_format

# Data fetching functions
from .data_fetcher import (
    fetch_and_analyze,
    fetch_data,
    get_supported_sources,
    get_source_info,
    DataFetcher
)

__all__ = [
    # Core functions
    "read_ticks", "normalize_schema", "compute_features",
    "rolling_forward_returns", "join_features_and_labels",
    
    # Simple API
    "Buffer",
    
    # Enhanced API
    "analyze_ticks", "convert_data", "quick_analysis", 
    "get_supported_presets", "validate_data_format",
    
    # Data fetching
    "fetch_and_analyze", "fetch_data", "get_supported_sources", 
    "get_source_info", "DataFetcher",
    
    # Feature utilities
    "get_feature_descriptions",
    
    # Version
    "__version__"
]
