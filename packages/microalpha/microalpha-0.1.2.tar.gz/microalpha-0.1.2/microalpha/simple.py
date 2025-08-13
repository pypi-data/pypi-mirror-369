# microalpha/simple.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Iterable
import numpy as np
import pandas as pd

from .features import compute_features
from .backtest import rolling_forward_returns, join_features_and_labels
from .convert import convert_file as _convert_file

CANON = ["timestamp","symbol","event_type","side","price","size",
         "best_bid","best_ask","bid_size","ask_size"]

def _to_ts(x, ts_unit: str):
    if isinstance(x, (int, np.integer, float, np.floating)):
        return pd.to_datetime(x, unit=ts_unit, errors="coerce")
    return pd.to_datetime(x, errors="coerce")

def _synth_spread(price: float) -> float:
    if price is None or np.isnan(price): return 0.01
    return max(0.0001 * abs(price), 0.01)

def _ensure_df(df: pd.DataFrame) -> pd.DataFrame:
    # Coerce types & index for canonical schema
    if "timestamp" not in df.columns:
        df = df.copy()
        df.columns = CANON[:len(df.columns)]
    for c in ["price","size","best_bid","best_ask","bid_size","ask_size"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if not isinstance(df.index, pd.DatetimeIndex):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).set_index("timestamp")
    return df.sort_index()

# ------------------------ Batch/easy mode ------------------------

def run(file: str | Path, *, ts_unit: str = "ms",
        window: str = "60s", horizon: str = "1s") -> pd.DataFrame:
    """
    One-liner: load a CSV in MicroAlpha schema and compute features+labels.
    """
    df = pd.read_csv(file)
    # If timestamp is numeric, use given unit; else parse strings
    if "timestamp" in df.columns:
        if np.issubdtype(df["timestamp"].dtype, np.number):
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit=ts_unit, errors="coerce")
        else:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = _ensure_df(df)

    feats  = compute_features(df, window=window)
    labels = rolling_forward_returns(df, horizon=horizon)
    return join_features_and_labels(feats, labels)

def convert(in_path: str | Path, out_path: str | Path, **kwargs) -> None:
    """
    Thin wrapper around convert_file so top-level API is simple:
    ma.convert("raw.csv","out.csv", symbol="BTCUSDT", preset="binance_kline", no_header=True, ts_unit="ms", time_col_idx=0)
    """
    _convert_file(str(in_path), str(out_path), **kwargs)

# ------------------------ Realtime/streaming ------------------------

@dataclass
class Buffer:
    window: str = "60s"
    horizon: str = "1s"
    ts_unit: str = "ms"
    buffer_seconds: Optional[int] = 900
    _df: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=CANON).set_index(pd.Index([], name="timestamp")))

    def _append_row(self, row: Dict) -> None:
        ts = row.get("timestamp")
        if ts is None:
            raise ValueError("row must include 'timestamp'")
        ts = _to_ts(ts, self.ts_unit)

        price = float(row.get("price", np.nan))
        size  = float(row.get("size", 1.0))
        bb    = row.get("best_bid")
        aa    = row.get("best_ask")
        if bb is None or aa is None:
            spr = _synth_spread(price)
            bb = price - spr/2 if bb is None else float(bb)
            aa = price + spr/2 if aa is None else float(aa)

        new = {
            "symbol": str(row.get("symbol", "SYMBOL")),
            "event_type": str(row.get("event_type", "trade")),
            "side": str(row.get("side", "")),
            "price": price,
            "size": size,
            "best_bid": float(bb),
            "best_ask": float(aa),
            "bid_size": float(row.get("bid_size", size if not np.isnan(size) else 1.0)),
            "ask_size": float(row.get("ask_size", size if not np.isnan(size) else 1.0)),
        }
        one = pd.DataFrame([new], index=[ts])
        self._df = pd.concat([self._df, one], axis=0).sort_index()

        if self.buffer_seconds is not None and len(self._df) > 0:
            cutoff = self._df.index[-1] - pd.Timedelta(seconds=self.buffer_seconds)
            self._df = self._df[self._df.index >= cutoff]

    def add(self, timestamp, *, price: float, size: float = 1.0, **kwargs) -> Optional[pd.Series]:
        """
        Minimal ergonomic call:
          buf.add(1735689600000, price=100.1, size=0.2, symbol='BTCUSDT')
        Returns the latest features row (pd.Series) or None until enough data.
        """
        row = dict(timestamp=timestamp, price=price, size=size, **kwargs)
        return self.add_row(row)

    def add_row(self, row: Dict) -> Optional[pd.Series]:
        self._append_row(row)
        try:
            feats  = compute_features(self._df, window=self.window)
            labels = rolling_forward_returns(self._df, horizon=self.horizon)
            ds     = join_features_and_labels(feats, labels)
            return None if ds.empty else ds.iloc[-1]
        except Exception:
            # Usually “not enough data yet” for the chosen window/horizon
            return None

    # helpers
    def latest(self) -> Optional[pd.Series]:
        try:
            feats  = compute_features(self._df, window=self.window)
            labels = rolling_forward_returns(self._df, horizon=self.horizon)
            ds     = join_features_and_labels(feats, labels)
            return None if ds.empty else ds.iloc[-1]
        except Exception:
            return None

    def to_frame(self) -> pd.DataFrame:
        return self._df.copy()
