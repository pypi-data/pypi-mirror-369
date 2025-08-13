"""
Enhanced schema converter with flexible timestamp selection, headerless CSV support,
and a preset for Binance kline files.

Canonical columns:
timestamp, symbol, event_type, side, price, size, best_bid, best_ask, bid_size, ask_size

Examples:
  # Headered CSV, specify timestamp column by name
  python -m microalpha.convert --in data/raw.csv --out data/my_ticks.csv --symbol BTCUSDT --time-col open_time --ts-unit ms

  # Headerless Binance kline CSV (1s candles), use preset
  python -m microalpha.convert --in BTCUSDT-1s-2023-07-01.csv --out data/my_ticks.csv --symbol BTCUSDT --preset binance_kline --no-header --ts-unit ms

  # Headerless generic CSV, take timestamp from column index (0-based)
  python -m microalpha.convert --in data/raw_no_header.csv --out data/my_ticks.csv --symbol ESU5 --no-header --time-col-idx 0 --ts-unit ms
"""

from __future__ import annotations
from pathlib import Path
import argparse
import pandas as pd
import numpy as np

CANON = ["timestamp","symbol","event_type","side","price","size","best_bid","best_ask","bid_size","ask_size"]

EVENT_MAP = {
    "trade": "trade", "t": "trade", "fill": "trade", "execution": "trade", "exec": "trade",
    "new": "add", "add": "add", "insert": "add", "update": "add", "u": "add",
    "cancel": "cancel", "delete": "cancel", "remove": "cancel", "cxl": "cancel",
}

SIDE_MAP = {
    "b": "buy", "buy": "buy", "bid": "buy",
    "s": "sell", "sell": "sell", "ask": "sell", "a": "sell",
}

PRICE_CANDS = ["price","p","last_price","trade_price","px","Value","close","Close"]
SIZE_CANDS  = ["size","qty","quantity","q","volume","vol","Volume"]
BID_CANDS   = ["best_bid","bid","bid_price","b","bestBid","BidPrice"]
ASK_CANDS   = ["best_ask","ask","ask_price","a","bestAsk","AskPrice"]
BIDSZ_CANDS = ["bid_size","bidsize","bid_sz","BidSize","bidQty"]
ASKSZ_CANDS = ["ask_size","asksize","ask_sz","AskSize","askQty"]
SYM_CANDS   = ["symbol","sym","ticker","instrument","pair"]
TIME_CANDS  = ["timestamp","ts","time","open_time","datetime","date","Date","event_time","T","Open time","Open Time"]
EVT_CANDS   = ["event_type","event","type","update_type","action","EventType"]

def _first_match(cols, candidates):
    cols_lower = {str(c).lower(): c for c in cols}  # handles int column names
    for cand in candidates:
        key = str(cand).lower()
        if key in cols_lower:
            return cols_lower[key]
    return None

def _infer_ts_unit_from_values(series: pd.Series) -> str | None:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    m = s.median()
    if m > 1e17: return "ns"
    if m > 1e11: return "ms"
    if m > 1e8:  return "s"
    return None

def _load_csv(path: str, no_header: bool) -> pd.DataFrame:
    return pd.read_csv(path, header=None if no_header else 'infer')

def _apply_preset(df: pd.DataFrame, preset: str) -> pd.DataFrame:
    if not preset: return df
    if preset.lower() == "binance_kline":
        cols = {
            0: "open_time", 1: "open", 2: "high", 3: "low", 4: "close",
            5: "volume", 6: "close_time"
        }
        if all(isinstance(c, int) for c in df.columns):
            df = df.rename(columns={i: cols.get(i, i) for i in df.columns})
    return df

def convert_df(df: pd.DataFrame, symbol: str | None = None, ts_unit: str | None = None,
               time_col: str | None = None, time_col_idx: int | None = None) -> pd.DataFrame:
    out = pd.DataFrame()

    # timestamp
    if time_col and time_col in df.columns:
        tcol = time_col
    elif time_col_idx is not None and time_col_idx in df.columns:
        tcol = time_col_idx
    else:
        tcol = _first_match(df.columns, TIME_CANDS)
    if tcol is None:
        raise ValueError("Could not find a timestamp column. Use --time-col, --time-col-idx, or --preset.")
    ts_series = df[tcol]

    if ts_unit is None:
        ts_unit = _infer_ts_unit_from_values(ts_series)
    if pd.api.types.is_string_dtype(ts_series) or ts_unit is None:
        out["timestamp"] = pd.to_datetime(ts_series, errors="coerce")
    else:
        out["timestamp"] = pd.to_datetime(ts_series, unit=ts_unit, errors="coerce")

    # symbol
    scol = _first_match(df.columns, SYM_CANDS)
    out["symbol"] = df[scol].astype(str) if scol else (symbol or "SYMBOL")

    # event_type
    ecol = _first_match(df.columns, EVT_CANDS)
    out["event_type"] = df[ecol].astype(str).str.lower().map(EVENT_MAP).fillna("trade") if ecol else "trade"

    # side
    side_col = _first_match(df.columns, ["side","direction","buyer_is_maker","isBuyerMaker","is_buyer_maker","is_maker_buyer"])
    if side_col:
        s = df[side_col]
        if s.dtype == bool or set(map(str, s.dropna().unique())).issubset({"True","False","true","false","0","1"}):
            out["side"] = ""
        else:
            out["side"] = s.astype(str).str.lower().map(SIDE_MAP).fillna("")
    else:
        out["side"] = ""

    # price & size
    pcol = _first_match(df.columns, PRICE_CANDS)
    qcol = _first_match(df.columns, SIZE_CANDS)
    out["price"] = pd.to_numeric(df[pcol], errors="coerce") if pcol else np.nan
    out["size"]  = pd.to_numeric(df[qcol], errors="coerce") if qcol else 1.0

    # best bid/ask
    bcol = _first_match(df.columns, BID_CANDS)
    acol = _first_match(df.columns, ASK_CANDS)
    bb = pd.to_numeric(df[bcol], errors="coerce") if bcol else np.nan
    aa = pd.to_numeric(df[acol], errors="coerce") if acol else np.nan
    spread = np.maximum(0.0001 * np.abs(out["price"]), 0.01)
    if bcol is None: bb = out["price"] - spread / 2
    if acol is None: aa = out["price"] + spread / 2
    out["best_bid"], out["best_ask"] = bb, aa

    # sizes
    bscol = _first_match(df.columns, BIDSZ_CANDS)
    ascol = _first_match(df.columns, ASKSZ_CANDS)
    out["bid_size"] = pd.to_numeric(df[bscol], errors="coerce") if bscol else out["size"].fillna(1.0)
    out["ask_size"] = pd.to_numeric(df[ascol], errors="coerce") if ascol else out["size"].fillna(1.0)

    # clean
    out = out[CANON].dropna(subset=["timestamp"])
    for c in ["price","size","best_bid","best_ask","bid_size","ask_size"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.sort_values("timestamp").reset_index(drop=True)

def convert_file(in_path: str, out_path: str, symbol: str | None = None, ts_unit: str | None = None,
                 time_col: str | None = None, time_col_idx: int | None = None,
                 preset: str | None = None, no_header: bool = False) -> None:
    df = _load_csv(in_path, no_header=no_header)
    df = _apply_preset(df, preset=preset)
    conv = convert_df(df, symbol=symbol, ts_unit=ts_unit, time_col=time_col, time_col_idx=time_col_idx)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    conv.to_csv(out_path, index=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--ts-unit", default=None, choices=["ns","ms","s"])
    ap.add_argument("--time-col", default=None)
    ap.add_argument("--time-col-idx", type=int, default=None)
    ap.add_argument("--preset", default=None, choices=["binance_kline"])
    ap.add_argument("--no-header", action="store_true")
    args = ap.parse_args()
    convert_file(args.inp, args.outp, symbol=args.symbol, ts_unit=args.ts_unit,
                 time_col=args.time_col, time_col_idx=args.time_col_idx,
                 preset=args.preset, no_header=args.no_header)
    print(f"Converted to {args.outp} with MicroAlpha schema.")

if __name__ == "__main__":
    main()
