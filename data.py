import yfinance as yf
import pandas as pd


def get_history(symbol: str, exchange: str = "NSE", period: str = "6mo") -> pd.DataFrame:
    """Stock ka price history laata hai. Baad me yahi function Dhan se data lega."""
    suffix = ".NS" if exchange == "NSE" else ".BO"
    df = yf.download(symbol.strip().upper() + suffix, period=period,
                     auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def get_many(symbols: list, period: str = "2y") -> dict:
    """Kai stocks ka data ek saath laata hai."""
    tickers = [s + ".NS" for s in symbols]
    raw = yf.download(tickers, period=period, auto_adjust=True,
                      progress=False, group_by="ticker", threads=True)
    out = {}
    for s, t in zip(symbols, tickers):
        try:
            df = raw[t].dropna()
            if len(df) > 30:
                out[s] = df
        except KeyError:
            pass
    return out