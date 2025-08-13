# microalpha/eda.py
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# seaborn is optional; if not installed we fall back to matplotlib heatmap
try:
    import seaborn as sns
    _HAS_SEABORN = True
except Exception:
    _HAS_SEABORN = False

CANON = [
    "timestamp", "symbol", "event_type", "side", "price", "size",
    "best_bid", "best_ask", "bid_size", "ask_size"
]

DEFAULT_FEATURE_COLS = [
    "trade_intensity", "qs_freq", "spread", "spread_vol", "obi", "rv", "fwd_ret"
]


# ------------------------------- Loading / Prep -------------------------------

def _read_ticks_robust(path: Path) -> pd.DataFrame:
    """
    Read a ticks/kline CSV into the canonical MicroAlpha schema.
    - If the file has headers and includes 'timestamp', use them.
    - If headerless (e.g., Binance klines), assign canonical names.
    Returns a DataFrame indexed by timestamp (DatetimeIndex), sorted by time.
    """
    # Peek to detect header
    try:
        tmp = pd.read_csv(path, nrows=5)
        has_ts = "timestamp" in tmp.columns
    except Exception:
        has_ts = False

    if has_ts:
        df = pd.read_csv(path)
    else:
        df = pd.read_csv(path, header=None, names=CANON)

    # Convert timestamp to datetime (assume ms if numeric; else parse)
    if np.issubdtype(df["timestamp"].dtype, np.number):
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Coerce numeric
    for c in ["price", "size", "best_bid", "best_ask", "bid_size", "ask_size"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").set_index("timestamp")
    return df


def load_features_or_compute(
    features_parquet: Path = Path("data/microalpha_features.parquet"),
    ticks_csv: Path = Path("data/my_ticks_all.csv"),
    window: str = "60s",
    horizon: str = "1s",
) -> pd.DataFrame:
    """
    Load previously computed features from a Parquet file if it exists.
    Otherwise, load ticks/kline CSV and compute features + labels with the given
    rolling window and horizon. Saves the Parquet for reuse.

    Parameters
    ----------
    features_parquet : Path
        Where to load/save features (Parquet).
    ticks_csv : Path
        Ticks/kline CSV to read if we need to compute.
    window : str
        Rolling window (e.g., '100ms', '10s', '60s').
        For 1-second klines, use '10s'–'120s'.
    horizon : str
        Forward return horizon (e.g., '100ms', '1s').

    Returns
    -------
    pd.DataFrame
        Feature dataframe indexed by timestamp, including 'fwd_ret'.
    """
    if features_parquet.exists():
        ds = pd.read_parquet(features_parquet)
        # Ensure DatetimeIndex
        if "timestamp" in ds.columns and not isinstance(ds.index, pd.DatetimeIndex):
            ds["timestamp"] = pd.to_datetime(ds["timestamp"], errors="coerce")
            ds = ds.set_index("timestamp").sort_index()
        return ds

    # Compute from ticks
    df = _read_ticks_robust(ticks_csv)

    from .features import compute_features
    from .backtest import rolling_forward_returns, join_features_and_labels

    feats = compute_features(df, window=window)
    labels = rolling_forward_returns(df, horizon=horizon)
    ds = join_features_and_labels(feats, labels).dropna(how="all")

    features_parquet.parent.mkdir(parents=True, exist_ok=True)
    ds.to_parquet(features_parquet)
    return ds


# --------------------------------- Plotting ----------------------------------

def plot_timeseries(
    ds: pd.DataFrame,
    show_mid: bool = True,
    show_rv: bool = True,
    show_spread: bool = True,
    figsize: Tuple[int, int] = (14, 4),
) -> None:
    """Plot key time series: mid, realized vol, spread & spread_vol."""
    if show_mid and "mid" in ds.columns:
        plt.figure(figsize=figsize)
        plt.plot(ds.index, ds["mid"], linewidth=1)
        plt.title("Midprice")
        plt.xlabel("Time")
        plt.ylabel("mid")
        plt.show()

    if show_rv and "rv" in ds.columns:
        plt.figure(figsize=figsize)
        plt.plot(ds.index, ds["rv"], linewidth=1)
        plt.title("Realized Vol (rolling)")
        plt.xlabel("Time")
        plt.ylabel("rv")
        plt.show()

    if show_spread:
        has_spread = "spread" in ds.columns
        has_spread_vol = "spread_vol" in ds.columns
        if has_spread or has_spread_vol:
            plt.figure(figsize=figsize)
            if has_spread:
                plt.plot(ds.index, ds["spread"], label="Spread", linewidth=1)
            if has_spread_vol:
                plt.plot(ds.index, ds["spread_vol"], label="Spread Vol", linewidth=1)
            plt.title("Spread & Spread Volatility")
            plt.xlabel("Time")
            plt.legend()
            plt.show()


def plot_correlation(
    ds: pd.DataFrame,
    cols: Sequence[str] = DEFAULT_FEATURE_COLS,
    figsize: Tuple[int, int] = (8, 6),
) -> None:
    """Correlation heatmap of selected columns (existing ones only)."""
    cols = [c for c in cols if c in ds.columns]
    if not cols:
        print("No matching columns to plot correlation.")
        return
    corr = ds[cols].corr()

    plt.figure(figsize=figsize)
    if _HAS_SEABORN:
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    else:
        # Matplotlib fallback
        im = plt.imshow(corr, interpolation="nearest", cmap="coolwarm")
        plt.colorbar(im)
        plt.xticks(range(len(cols)), cols, rotation=45, ha="right")
        plt.yticks(range(len(cols)), cols)
        for i in range(len(cols)):
            for j in range(len(cols)):
                plt.text(j, i, f"{corr.values[i,j]:.2f}",
                         ha="center", va="center", color="black")
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.show()


def plot_spike_zoom(
    ds: pd.DataFrame,
    feature: str = "qs_freq",
    quantile: float = 0.99,
    span: str = "2s",
    also_plot: Optional[Iterable[str]] = ("obi",),
) -> None:
    """
    Zoom around the first spike of `feature` above given quantile.
    `span` is total width (e.g., '2s' = 1s before + 1s after).
    """
    if feature not in ds.columns:
        print(f"Feature '{feature}' not in dataframe; available: {list(ds.columns)}")
        return

    threshold = ds[feature].quantile(quantile)
    spikes = ds[ds[feature] > threshold]
    if spikes.empty:
        print(f"No spikes above q={quantile} found for '{feature}'.")
        return

    center = spikes.index[0]
    half = pd.Timedelta(span) / 2
    z = ds[(ds.index >= center - half) & (ds.index <= center + half)]

    plt.figure(figsize=(14, 4))
    plt.plot(z.index, z[feature], label=feature, marker="o", linewidth=1)
    if also_plot:
        for col in also_plot:
            if col in z.columns:
                plt.plot(z.index, z[col], label=col, linewidth=1)
    plt.title(f"Zoomed around {feature} spike @ {center}")
    plt.xlabel("Time")
    plt.legend()
    plt.show()


def save_all_plots(
    ds: pd.DataFrame,
    outdir: Path | str = "reports",
    prefix: str = "eda",
    include_corr: bool = True,
) -> None:
    """
    Save key plots as PNGs under `outdir`.
    """
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    # Mid
    if "mid" in ds.columns:
        plt.figure(figsize=(14, 4))
        plt.plot(ds.index, ds["mid"], linewidth=1)
        plt.title("Midprice")
        plt.xlabel("Time")
        plt.ylabel("mid")
        plt.tight_layout()
        plt.savefig(out / f"{prefix}_mid.png", dpi=160)
        plt.close()

    # RV
    if "rv" in ds.columns:
        plt.figure(figsize=(14, 4))
        plt.plot(ds.index, ds["rv"], linewidth=1)
        plt.title("Realized Vol (rolling)")
        plt.xlabel("Time")
        plt.ylabel("rv")
        plt.tight_layout()
        plt.savefig(out / f"{prefix}_rv.png", dpi=160)
        plt.close()

    # Spread & Spread Vol
    if "spread" in ds.columns or "spread_vol" in ds.columns:
        plt.figure(figsize=(14, 4))
        if "spread" in ds.columns:
            plt.plot(ds.index, ds["spread"], label="Spread", linewidth=1)
        if "spread_vol" in ds.columns:
            plt.plot(ds.index, ds["spread_vol"], label="Spread Vol", linewidth=1)
        plt.title("Spread & Spread Volatility")
        plt.xlabel("Time")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out / f"{prefix}_spread.png", dpi=160)
        plt.close()

    # Correlation heatmap
    if include_corr:
        cols = [c for c in DEFAULT_FEATURE_COLS if c in ds.columns]
        if cols:
            corr = ds[cols].corr()
            plt.figure(figsize=(8, 6))
            if _HAS_SEABORN:
                sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
            else:
                im = plt.imshow(corr, interpolation="nearest", cmap="coolwarm")
                plt.colorbar(im)
                plt.xticks(range(len(cols)), cols, rotation=45, ha="right")
                plt.yticks(range(len(cols)), cols)
                for i in range(len(cols)):
                    for j in range(len(cols)):
                        plt.text(j, i, f"{corr.values[i,j]:.2f}",
                                 ha="center", va="center", color="black")
            plt.title("Feature Correlation Heatmap")
            plt.tight_layout()
            plt.savefig(out / f"{prefix}_corr.png", dpi=160)
            plt.close()


__all__ = [
    "load_features_or_compute",
    "plot_timeseries",
    "plot_correlation",
    "plot_spike_zoom",
    "save_all_plots",
]
