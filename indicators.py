import numpy as np
import pandas as pd


# ---------- Building blocks ----------
def sma(close, period=20):
    return close.rolling(period).mean()


def ema(close, period=20):
    return close.ewm(span=period, adjust=False).mean()


def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss)


def macd(close, fast=12, slow=26, signal=9):
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig, line - sig


def bollinger(close, period=20, std=2):
    mid = close.rolling(period).mean()
    sd = close.rolling(period).std()
    return mid + std * sd, mid, mid - std * sd


def true_range(df):
    prev = df["Close"].shift()
    return pd.concat([df["High"] - df["Low"],
                      (df["High"] - prev).abs(),
                      (df["Low"] - prev).abs()], axis=1).max(axis=1)


def atr(df, period=14):
    return true_range(df).ewm(alpha=1 / period, adjust=False).mean()


def stochastic(df, period=14, smooth=3):
    low = df["Low"].rolling(period).min()
    high = df["High"].rolling(period).max()
    k = 100 * (df["Close"] - low) / (high - low)
    return k, k.rolling(smooth).mean()


def adx(df, period=14):
    up = df["High"].diff()
    down = -df["Low"].diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    a = atr(df, period)
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / a
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / a
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    return dx.ewm(alpha=1 / period, adjust=False).mean()


def cci(df, period=20):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    ma = tp.rolling(period).mean()
    md = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (tp - ma) / (0.015 * md)


def williams_r(df, period=14):
    high = df["High"].rolling(period).max()
    low = df["Low"].rolling(period).min()
    return -100 * (high - df["Close"]) / (high - low)


def roc(close, period=12):
    return close.pct_change(period) * 100


def obv(df):
    direction = np.sign(df["Close"].diff()).fillna(0)
    return (direction * df["Volume"]).cumsum()


# ---------- Registry ----------
def _num(default, lo, hi):
    """User ke liye number input ki setting."""
    return {"default": default, "min": lo, "max": hi}


def _choice(options):
    """User ke liye dropdown ki setting."""
    return {"options": options}


def _macd_pick(d, p):
    line, sig, hist = macd(d["Close"], p["fast"], p["slow"], p["signal"])
    return {"MACD line": line, "Signal line": sig, "Histogram": hist}[p["line"]]


def _bb_pick(d, p):
    up, mid, low = bollinger(d["Close"], p["period"], p["std"])
    return {"Upper": up, "Middle": mid, "Lower": low}[p["band"]]


def _stoch_pick(d, p):
    k, dd = stochastic(d, p["period"], p["smooth"])
    return k if p["line"] == "%K" else dd


INDICATORS = {
    "Price": {
        "params": {"field": _choice(["Close", "Open", "High", "Low"])},
        "fn": lambda d, p: d[p["field"]],
        "help": "Stock ka price. Close, Open, High ya Low chun sakte ho."},
    "SMA": {
        "params": {"period": _num(20, 1, 300)},
        "fn": lambda d, p: sma(d["Close"], p["period"]),
        "help": "Simple moving average: pichhle N din ke closing price ka average."},
    "EMA": {
        "params": {"period": _num(20, 1, 300)},
        "fn": lambda d, p: ema(d["Close"], p["period"]),
        "help": "Exponential moving average. Naye prices ko zyada weight deta hai."},
    "RSI": {
        "params": {"period": _num(14, 2, 100)},
        "fn": lambda d, p: rsi(d["Close"], p["period"]),
        "help": "0 se 100. Aam taur par 30 se neeche oversold, 70 se upar overbought maana jata hai."},
    "MACD": {
        "params": {"fast": _num(12, 2, 100), "slow": _num(26, 3, 200),
                   "signal": _num(9, 2, 100),
                   "line": _choice(["MACD line", "Signal line", "Histogram"])},
        "fn": _macd_pick,
        "help": "Do EMA ka farak. Histogram positive ho toh momentum upar ki taraf hai."},
    "Bollinger Bands": {
        "params": {"period": _num(20, 2, 200), "std": _num(2.0, 0.5, 5.0),
                   "band": _choice(["Upper", "Middle", "Lower"])},
        "fn": _bb_pick,
        "help": "Average ke upar aur neeche standard deviation wale band. Price band ke bahar jaaye toh stretched maana jata hai."},
    "Stochastic": {
        "params": {"period": _num(14, 2, 100), "smooth": _num(3, 1, 20),
                   "line": _choice(["%K", "%D"])},
        "fn": _stoch_pick,
        "help": "Price apni N din ki range me kahan hai. Aam taur par 20 se neeche oversold, 80 se upar overbought."},
    "ADX": {
        "params": {"period": _num(14, 2, 100)},
        "fn": lambda d, p: adx(d, p["period"]),
        "help": "Trend kitna mazboot hai. 25 se upar strong trend. Direction nahi batata."},
    "ATR": {
        "params": {"period": _num(14, 2, 100)},
        "fn": lambda d, p: atr(d, p["period"]),
        "help": "Roz ki average price range. Stop loss tay karne me kaam aata hai."},
    "CCI": {
        "params": {"period": _num(20, 2, 100)},
        "fn": lambda d, p: cci(d, p["period"]),
        "help": "Aam taur par -100 se neeche oversold, +100 se upar overbought."},
    "Williams %R": {
        "params": {"period": _num(14, 2, 100)},
        "fn": lambda d, p: williams_r(d, p["period"]),
        "help": "-80 se neeche oversold, -20 se upar overbought maana jata hai."},
    "ROC": {
        "params": {"period": _num(12, 1, 200)},
        "fn": lambda d, p: roc(d["Close"], p["period"]),
        "help": "N din me price kitne percent badla."},
    "Return %": {
        "params": {"days": _num(21, 1, 300)},
        "fn": lambda d, p: d["Close"].pct_change(p["days"]) * 100,
        "help": "N trading din ka return. 21 din lagbhag 1 mahina hota hai."},
    "Volume": {
        "params": {},
        "fn": lambda d, p: d["Volume"],
        "help": "Traded volume."},
    "Volume vs average": {
        "params": {"period": _num(20, 2, 200)},
        "fn": lambda d, p: d["Volume"] / d["Volume"].rolling(p["period"]).mean(),
        "help": "Volume apne N din ke average ka kitna guna hai. 2 matlab double."},
    "OBV": {
        "params": {},
        "fn": lambda d, p: obv(d),
        "help": "Volume ka cumulative flow. Badhta OBV matlab buying pressure."},
    "% from N-day high": {
        "params": {"days": _num(252, 5, 300)},
        "fn": lambda d, p: (d["Close"] / d["Close"].rolling(p["days"]).max() - 1) * 100,
        "help": "N din ke high se kitna neeche (negative number). 0 matlab high pe hai."},
    "% from N-day low": {
        "params": {"days": _num(252, 5, 300)},
        "fn": lambda d, p: (d["Close"] / d["Close"].rolling(p["days"]).min() - 1) * 100,
        "help": "N din ke low se kitna upar."},
}


def compute(df, name, params, ago=0):
    """Ek stock ke liye indicator ki value. ago=0 matlab aaj, 1 matlab kal."""
    try:
        series = INDICATORS[name]["fn"](df, params)
        return float(series.iloc[-1 - ago])
    except Exception:
        return float("nan")


def label(name, params, ago=0):
    text = name
    if params:
        text += " (" + ", ".join(str(v) for v in params.values()) + ")"
    if ago:
        text += f" [{ago}d ago]"
    return text