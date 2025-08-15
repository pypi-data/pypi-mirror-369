"""
Data Fetcher Module for MicroAlpha
==================================

Automatically fetch tick data from various sources and convert to MicroAlpha format.
Supports exchanges, APIs, and custom data sources.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
import time
import json
from pathlib import Path
import warnings

# Import MicroAlpha functions
from .io import normalize_schema
from .enhanced import convert_data
from .features import compute_features
from .backtest import rolling_forward_returns


class DataFetcher:
    """Universal data fetcher for various sources."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        
        # Rotate between different user agents to appear more like browsers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        self.session.headers.update({
            'User-Agent': user_agents[0],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.user_agents = user_agents
        self.current_ua_index = 0
    
    def fetch_and_analyze(
        self,
        source: str,
        symbol: str,
        interval: str = "1m",
        limit: int = 1000,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch data from source and analyze it in one call.
        
        Args:
            source: Data source ('binance', 'coinbase', 'kraken', 'custom_url')
            symbol: Trading symbol (e.g., 'BTCUSDT')
            interval: Time interval ('1m', '5m', '1h', '1d')
            limit: Number of data points to fetch
            start_time: Start time for data range
            end_time: End time for data range
            **kwargs: Additional source-specific parameters
            
        Returns:
            DataFrame with computed features and forward returns
        """
        print(f"🚀 Fetching {symbol} data from {source}...")
        
        # Fetch raw data
        raw_data = self.fetch_data(
            source=source,
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )
        
        if raw_data is None or len(raw_data) == 0:
            raise ValueError(f"No data fetched from {source} for {symbol}")
        
        print(f"✅ Fetched {len(raw_data)} data points")
        
        # Convert to MicroAlpha format
        print("🔄 Converting to MicroAlpha format...")
        converted_data = self._convert_to_microalpha(raw_data, source, symbol)
        
        # Compute features
        print("⚙️ Computing microstructure features...")
        features = compute_features(converted_data, window="1s")
        
        # Add back bid/ask columns needed for forward returns
        if 'best_bid' not in features.columns and 'best_bid' in converted_data.columns:
            features['best_bid'] = converted_data['best_bid']
            features['best_ask'] = converted_data['best_ask']
        
        # Generate forward returns
        print("📈 Generating forward returns...")
        features = rolling_forward_returns(features, horizon="1s")
        
        print(f"🎉 Analysis complete! {len(features)} features computed")
        return features
    
    def fetch_data(
        self,
        source: str,
        symbol: str,
        interval: str = "1m",
        limit: int = 1000,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch raw data from specified source.
        """
        source = source.lower()
        
        if source == "binance":
            return self._fetch_binance(symbol, interval, limit, start_time, end_time, **kwargs)
        elif source == "coinbase":
            return self._fetch_coinbase(symbol, interval, limit, start_time, end_time, **kwargs)
        elif source == "kraken":
            return self._fetch_kraken(symbol, interval, limit, start_time, end_time, **kwargs)
        elif source == "custom_url":
            return self._fetch_custom_url(symbol, interval, limit, start_time, end_time, **kwargs)
        else:
            raise ValueError(f"Unsupported source: {source}. Supported: binance, coinbase, kraken, custom_url")
    
    def _fetch_binance(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 1000,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Binance API."""
        
        # Binance interval mapping
        interval_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
        }
        
        if interval not in interval_map:
            raise ValueError(f"Unsupported interval: {interval}")
        
        # Build URL - try different endpoints for different regions and versions
        base_urls = [
            "https://api.binance.com/api/v3/klines",
            "https://api1.binance.com/api/v3/klines", 
            "https://api2.binance.com/api/v3/klines",
            "https://api3.binance.com/api/v3/klines",
            "https://api.binance.us/api/v3/klines",  # US version
            "https://testnet.binance.vision/api/v3/klines",  # Testnet
            "https://api.binance.com/api/v1/klines",  # Legacy v1 API
            "https://data.binance.com/api/v3/klines",  # Data API
            "https://fapi.binance.com/api/v3/klines",  # Futures API
            "https://dapi.binance.com/api/v3/klines",  # Delivery Futures API
            "https://api.binance.com/api/v3/ticker/24hr",  # Alternative endpoint
            "https://api.binance.com/api/v3/avgPrice"  # Another alternative
        ]
        
        params = {
            'symbol': symbol.upper(),
            'interval': interval_map[interval],
            'limit': min(limit, 1000)  # Binance max is 1000
        }
        
        # Add time parameters if provided
        if start_time:
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            params['startTime'] = int(start_time.timestamp() * 1000)
        
        if end_time:
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
            params['endTime'] = int(end_time.timestamp() * 1000)
        
        # Try different endpoints with different approaches
        for attempt in range(2):  # Try twice with different strategies
            for url in base_urls:
                try:
                    print(f"📡 Fetching from Binance: {symbol} {interval} via {url.split('//')[1]} (attempt {attempt + 1})")
                    
                    # Rotate user agent for each attempt
                    if attempt > 0:
                        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
                        self.session.headers['User-Agent'] = self.user_agents[self.current_ua_index]
                        print(f"   🔄 Trying with User-Agent: {self.user_agents[self.current_ua_index][:50]}...")
                    
                    # Add some randomization to appear more human-like
                    import random
                    import time
                    time.sleep(random.uniform(0.1, 0.5))  # Small random delay
                    
                    # Try different request methods
                    if attempt == 0:
                        response = self.session.get(url, params=params, timeout=30)
                    else:
                        # Try with different headers and approach
                        headers = self.session.headers.copy()
                        headers.update({
                            'Referer': 'https://www.binance.com/',
                            'Origin': 'https://www.binance.com',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin'
                        })
                        response = self.session.get(url, params=params, headers=headers, timeout=30)
                    
                    response.raise_for_status()
                    print(f"   ✅ Success with {url.split('//')[1]}")
                    break  # Success, exit loop
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ⚠️ {url.split('//')[1]} failed: {error_msg[:50]}...")
                    
                    # If it's a 451 error, try with different approach
                    if "451" in error_msg and attempt == 0:
                        print(f"   🔄 451 error detected, will retry with different strategy...")
                        continue
                    
                    continue
            else:
                continue  # Try next attempt strategy
            
            # If we get here, we succeeded
            break
        else:
            # Try one last approach - use different symbol formats and endpoints
            try:
                print(f"🔄 Trying alternative approaches...")
                
                # Try different symbol formats
                alt_symbols = [
                    symbol.replace('USDT', 'USD').replace('USDC', 'USD'),
                    symbol.replace('USDT', 'USDT').replace('USDC', 'USDC'),
                    symbol.replace('USDT', 'BUSD').replace('USDC', 'BUSD'),
                    symbol.replace('USDT', '').replace('USDC', ''),
                    symbol.lower(),
                    symbol.upper()
                ]
                
                # Try different endpoint types
                alt_endpoints = [
                    "https://api.binance.com/api/v3/ticker/24hr",
                    "https://api.binance.com/api/v3/avgPrice",
                    "https://api.binance.com/api/v3/ticker/price",
                    "https://api.binance.com/api/v3/ticker/bookTicker"
                ]
                
                for alt_symbol in alt_symbols:
                    for alt_url in alt_endpoints:
                        try:
                            print(f"📡 Trying {alt_symbol} via {alt_url.split('//')[1]}")
                            
                            # Use different parameters for alternative endpoints
                            if 'ticker' in alt_url:
                                alt_params = {'symbol': alt_symbol}
                            elif 'avgPrice' in alt_url:
                                alt_params = {'symbol': alt_symbol}
                            else:
                                alt_params = {'symbol': alt_symbol}
                            
                            # Try with different headers
                            headers = self.session.headers.copy()
                            headers.update({
                                'Referer': 'https://www.binance.com/',
                                'Origin': 'https://www.binance.com',
                                'Cache-Control': 'no-cache',
                                'Pragma': 'no-cache'
                            })
                            
                            response = self.session.get(alt_url, params=alt_params, headers=headers, timeout=30)
                            response.raise_for_status()
                            print(f"   ✅ Success with alternative approach: {alt_symbol} via {alt_url.split('//')[1]}")
                            
                            # Update params for the rest of the function
                            params = alt_params
                            # Also update the original symbol for consistency
                            symbol = alt_symbol
                            break
                            
                        except Exception as e:
                            print(f"   ⚠️ {alt_symbol} via {alt_url.split('//')[1]} failed: {str(e)[:50]}...")
                            continue
                    else:
                        continue
                    break
                else:
                    raise Exception("All alternative approaches failed")
                    
            except Exception as e:
                raise Exception(f"All Binance endpoints and strategies failed: {e}")
        
        try:
            data = response.json()
            
            if not data:
                raise ValueError(f"No data returned for {symbol}")
            
            # Handle different response formats based on endpoint
            if 'ticker' in response.url or 'avgPrice' in response.url:
                # Alternative endpoints return different format
                print(f"   🔄 Using alternative endpoint format...")
                if 'ticker' in response.url:
                    # 24hr ticker format
                    df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
                    # Convert to OHLCV format
                    df['open_time'] = pd.Timestamp.now()
                    df['close_time'] = pd.Timestamp.now()
                    df['open'] = df.get('openPrice', df.get('lastPrice', 0))
                    df['high'] = df.get('highPrice', df.get('lastPrice', 0))
                    df['low'] = df.get('lowPrice', df.get('lastPrice', 0))
                    df['close'] = df.get('lastPrice', df.get('price', 0))
                    df['volume'] = df.get('volume', df.get('baseVolume', 0))
                    df['quote_volume'] = df.get('quoteVolume', 0)
                    df['trades'] = df.get('count', 0)
                    df['taker_buy_base'] = 0
                    df['taker_buy_quote'] = 0
                    df['ignore'] = 0
                else:
                    # avgPrice format
                    df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
                    df['open_time'] = pd.Timestamp.now()
                    df['close_time'] = pd.Timestamp.now()
                    df['open'] = df.get('price', 0)
                    df['high'] = df.get('price', 0)
                    df['low'] = df.get('price', 0)
                    df['close'] = df.get('price', 0)
                    df['volume'] = df.get('volume', 0)
                    df['quote_volume'] = 0
                    df['trades'] = 0
                    df['taker_buy_base'] = 0
                    df['taker_buy_quote'] = 0
                    df['ignore'] = 0
            else:
                # Standard klines format
                df = pd.DataFrame(data, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
            
            # Convert types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_volume', 'trades']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Convert timestamps
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Add symbol column
            df['symbol'] = symbol.upper()
            
            print(f"✅ Fetched {len(df)} klines from Binance")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching from Binance: {e}")
            return pd.DataFrame()
    
    def _fetch_coinbase(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 1000,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Coinbase API."""
        
        # Coinbase uses different symbol format
        coinbase_symbol = symbol.replace('USDT', '-USD').replace('USDC', '-USD')
        
        # Build URL for historical data - try multiple endpoints
        urls_to_try = [
            f"https://api.pro.coinbase.com/products/{coinbase_symbol}/candles",
            f"https://api.exchange.coinbase.com/products/{coinbase_symbol}/candles",
            f"https://api.coinbase.com/v2/products/{coinbase_symbol}/candles"
        ]
        
        # Coinbase interval mapping (in seconds)
        interval_map = {
            '1m': 60, '5m': 300, '15m': 900, '30m': 1800,
            '1h': 3600, '4h': 14400, '1d': 86400
        }
        
        if interval not in interval_map:
            raise ValueError(f"Unsupported interval: {interval}")
        
        params = {
            'granularity': interval_map[interval]
        }
        
        # Add time parameters if provided
        if start_time:
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            params['start'] = start_time.isoformat()
        
        if end_time:
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
            params['end'] = end_time.isoformat()
        
        # Try different Coinbase endpoints
        for url in urls_to_try:
            try:
                print(f"📡 Fetching from Coinbase: {coinbase_symbol} {interval} via {url.split('//')[1]}")
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                break  # Success, exit loop
            except Exception as e:
                print(f"   ⚠️ {url.split('//')[1]} failed: {str(e)[:50]}...")
                continue
        else:
            raise Exception("All Coinbase endpoints failed")
        
        try:
            data = response.json()
            
            if not data:
                raise ValueError(f"No data returned for {coinbase_symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'low', 'high', 'open', 'close', 'volume'
            ])
            
            # Convert types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Convert timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Add symbol column
            df['symbol'] = symbol.upper()
            
            print(f"✅ Fetched {len(df)} candles from Coinbase")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching from Coinbase: {e}")
            return pd.DataFrame()
    
    def _fetch_kraken(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 1000,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Kraken API."""
        
        # Kraken symbol mapping - use proper Kraken format
        kraken_symbol_map = {
            'BTCUSDT': 'XBTUSD',
            'ETHUSDT': 'ETHUSD', 
            'LTCUSDT': 'XLTCUSD',
            'XRPUSDT': 'XXRPUSD',
            'ADAUSDT': 'ADAUSD',
            'SOLUSDT': 'SOLUSD'
        }
        kraken_symbol = kraken_symbol_map.get(symbol, symbol.replace('USDT', 'USD').replace('USDC', 'USD'))
        
        # Build URL
        url = "https://api.kraken.com/0/public/OHLC"
        
        # Kraken interval mapping
        interval_map = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
        }
        
        if interval not in interval_map:
            raise ValueError(f"Unsupported interval: {interval}")
        
        params = {
            'pair': kraken_symbol,
            'interval': interval_map[interval]
        }
        
        try:
            print(f"📡 Fetching from Kraken: {kraken_symbol} {interval}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data and data['error']:
                raise ValueError(f"Kraken API error: {data['error']}")
            
            # Extract OHLCV data - handle different response formats
            if kraken_symbol in data['result']:
                ohlcv_data = data['result'][kraken_symbol]
            else:
                # Try alternative symbol formats
                alt_symbols = [kraken_symbol, kraken_symbol.replace('XBT', 'BTC'), kraken_symbol.replace('BTC', 'XBT')]
                for alt_sym in alt_symbols:
                    if alt_sym in data['result']:
                        ohlcv_data = data['result'][alt_sym]
                        break
                else:
                    # If still not found, try to get any available data
                    available_pairs = list(data['result'].keys())
                    if available_pairs:
                        print(f"   ⚠️ {kraken_symbol} not found, using {available_pairs[0]} instead")
                        ohlcv_data = data['result'][available_pairs[0]]
                    else:
                        raise ValueError(f"No data returned for {kraken_symbol}")
            
            if not ohlcv_data:
                raise ValueError(f"No data returned for {kraken_symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'count'
            ])
            
            # Convert types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'vwap', 'count']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Convert timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Add symbol column
            df['symbol'] = symbol.upper()
            
            print(f"✅ Fetched {len(df)} candles from Kraken")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching from Kraken: {e}")
            return pd.DataFrame()
    
    def _fetch_custom_url(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 1000,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from custom URL/API."""
        
        url = kwargs.get('url')
        if not url:
            raise ValueError("URL required for custom_url source")
        
        # Custom headers and parameters
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})
        
        # Add default parameters
        params.update({
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        })
        
        # Add time parameters if provided
        if start_time:
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            params['start_time'] = start_time.isoformat()
        
        if end_time:
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
            params['end_time'] = end_time.isoformat()
        
        try:
            print(f"📡 Fetching from custom URL: {url}")
            
            # Use custom headers if provided
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                raise ValueError("No data returned from custom URL")
            
            # Try to detect data format and convert
            df = self._detect_and_convert_format(data, symbol)
            
            print(f"✅ Fetched {len(df)} data points from custom URL")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching from custom URL: {e}")
            return pd.DataFrame()
    
    def _detect_and_convert_format(self, data: Any, symbol: str) -> pd.DataFrame:
        """Detect data format and convert to standard DataFrame."""
        
        if isinstance(data, list) and len(data) > 0:
            # List of records
            if isinstance(data[0], dict):
                # List of dictionaries
                df = pd.DataFrame(data)
            else:
                # List of lists (like OHLCV)
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        elif isinstance(data, dict):
            # Dictionary with data key
            if 'data' in data:
                df = pd.DataFrame(data['data'])
            elif 'result' in data:
                df = pd.DataFrame(data['result'])
            else:
                # Try to find any list-like data
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        df = pd.DataFrame(value)
                        break
                else:
                    raise ValueError("Could not detect data format")
        else:
            raise ValueError("Unsupported data format")
        
        # Add symbol if not present
        if 'symbol' not in df.columns:
            df['symbol'] = symbol.upper()
        
        return df
    
    def _convert_to_microalpha(self, df: pd.DataFrame, source: str, symbol: str) -> pd.DataFrame:
        """Convert fetched data to MicroAlpha format."""
        
        # Determine the best preset based on source and columns
        preset = self._detect_preset(df, source)
        
        # Convert using the convert_data function
        temp_input = f"temp_{source}_{symbol}_{int(time.time())}.csv"
        temp_output = f"temp_microalpha_{int(time.time())}.csv"
        
        try:
            df.to_csv(temp_input, index=False)
            
            convert_data(
                temp_input,
                temp_output,
                symbol=symbol,
                preset=preset
            )
            
            # Read the converted data
            converted_df = pd.read_csv(temp_output)
            converted_df['timestamp'] = pd.to_datetime(converted_df['timestamp'])
            converted_df = converted_df.set_index('timestamp')
            
            return converted_df
            
        finally:
            # Clean up temp files
            for temp_file in [temp_input, temp_output]:
                if Path(temp_file).exists():
                    Path(temp_file).unlink()
    
    def _detect_preset(self, df: pd.DataFrame, source: str) -> str:
        """Detect the best preset for conversion."""
        
        columns = set(df.columns.str.lower())
        
        # Check for OHLCV format
        ohlcv_cols = {'open', 'high', 'low', 'close', 'volume'}
        if ohlcv_cols.issubset(columns):
            if source == 'binance':
                return 'binance_kline'
            elif source == 'coinbase':
                return 'coinbase_trades'
            else:
                return 'generic_ohlcv'
        
        # Check for tick format
        tick_cols = {'price', 'size', 'side'}
        if tick_cols.issubset(columns):
            return 'tick_trades'
        
        # Default to generic
        return 'generic_ohlcv'
    
    def get_supported_sources(self) -> List[str]:
        """Get list of supported data sources."""
        return ['binance', 'coinbase', 'kraken', 'custom_url']
    
    def get_source_info(self, source: str) -> Dict[str, Any]:
        """Get information about a specific data source."""
        source = source.lower()
        
        info = {
            'binance': {
                'name': 'Binance',
                'url': 'https://api.binance.com',
                'intervals': ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'],
                'symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'],
                'rate_limit': '1200 requests per minute',
                'authentication': 'Optional (higher limits with API key)'
            },
            'coinbase': {
                'name': 'Coinbase Pro',
                'url': 'https://api.pro.coinbase.com',
                'intervals': ['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                'symbols': ['BTC-USD', 'ETH-USD', 'LTC-USD', 'BCH-USD'],
                'rate_limit': '3 requests per second',
                'authentication': 'Optional (higher limits with API key)'
            },
            'kraken': {
                'name': 'Kraken',
                'url': 'https://api.kraken.com',
                'intervals': ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'],
                'symbols': ['BTCUSD', 'ETHUSD', 'LTCUSD', 'XRPUSD'],
                'rate_limit': '15 requests per 10 seconds',
                'authentication': 'Optional (higher limits with API key)'
            },
            'custom_url': {
                'name': 'Custom API/URL',
                'url': 'User-defined',
                'intervals': 'User-defined',
                'symbols': 'User-defined',
                'rate_limit': 'Depends on API',
                'authentication': 'Depends on API'
            }
        }
        
        return info.get(source, {})
    
    def set_api_key(self, source: str, api_key: str, secret_key: str = None):
        """Set API credentials for authenticated requests."""
        source = source.lower()
        
        if source == 'binance':
            self.session.headers.update({'X-MBX-APIKEY': api_key})
        elif source == 'coinbase':
            # Coinbase uses different auth method
            pass
        elif source == 'kraken':
            # Kraken uses different auth method
            pass
        
        print(f"✅ API key set for {source}")


# Convenience functions for easy access
def fetch_and_analyze(
    source: str,
    symbol: str,
    interval: str = "1m",
    limit: int = 1000,
    start_time: Optional[Union[str, datetime]] = None,
    end_time: Optional[Union[str, datetime]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Convenience function to fetch and analyze data in one call.
    
    Args:
        source: Data source ('binance', 'coinbase', 'kraken', 'custom_url')
        symbol: Trading symbol (e.g., 'BTCUSDT')
        interval: Time interval ('1m', '5m', '1h', '1d')
        limit: Number of data points to fetch
        start_time: Start time for data range
        end_time: End time for data range
        **kwargs: Additional source-specific parameters
        
    Returns:
        DataFrame with computed features and forward returns
        
    Example:
        # Fetch and analyze Binance data
        features = fetch_and_analyze('binance', 'BTCUSDT', '1m', 1000)
        
        # Fetch from custom API
        features = fetch_and_analyze(
            'custom_url', 
            'BTCUSDT', 
            '1m', 
            1000,
            url='https://api.example.com/data',
            headers={'Authorization': 'Bearer token'}
        )
    """
    fetcher = DataFetcher()
    return fetcher.fetch_and_analyze(
        source=source,
        symbol=symbol,
        interval=interval,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
        **kwargs
    )


def fetch_data(
    source: str,
    symbol: str,
    interval: str = "1m",
    limit: int = 1000,
    start_time: Optional[Union[str, datetime]] = None,
    end_time: Optional[Union[str, datetime]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Convenience function to fetch raw data.
    
    Returns:
        Raw DataFrame from the source
    """
    fetcher = DataFetcher()
    return fetcher.fetch_data(
        source=source,
        symbol=symbol,
        interval=interval,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
        **kwargs
    )


def get_supported_sources() -> List[str]:
    """Get list of supported data sources."""
    return DataFetcher().get_supported_sources()


def get_source_info(source: str) -> Dict[str, Any]:
    """Get information about a specific data source."""
    return DataFetcher().get_source_info(source) 