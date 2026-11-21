import streamlit as st
import pandas as pd
from data import get_many
from indicators import rsi, sma
from stocks import NIFTY_LARGE

st.set_page_config(page_title="Screener", page_icon="🔍", layout="wide")
st.title("🔍 Stock Screener")
st.caption("Large-cap NSE stocks par apne filters lagao.")


@st.cache_data(ttl=600)
def load_data():
    return get_many(NIFTY_LARGE)


c1, c2, c3 = st.columns(3)
rsi_low, rsi_high = c1.slider("RSI range", 0, 100, (0, 40))
above_200 = c2.checkbox("Price 200-day average ke upar ho")
min_vol = c3.number_input("Minimum volume", value=0, step=100000)

data = load_data()

rows = []
for sym, df in data.items():
    close = df["Close"]
    last = close.iloc[-1]
    r = rsi(close).iloc[-1]
    s200 = sma(close, 200).iloc[-1]
    vol = df["Volume"].iloc[-1]
    rows.append({
        "Symbol": sym,
        "Price": round(last, 2),
        "RSI (14)": round(r, 1),
        "200-day avg": round(s200, 2) if pd.notna(s200) else None,
        "Volume": int(vol),
    })

table = pd.DataFrame(rows)

mask = table["RSI (14)"].between(rsi_low, rsi_high) & (table["Volume"] >= min_vol)
if above_200:
    mask &= table["Price"] > table["200-day avg"]

result = table[mask].sort_values("RSI (14)")
st.write(f"**{len(result)}** stocks match (total {len(table)} scan hue)")
st.dataframe(result, hide_index=True)

st.divider()
st.caption("For educational purposes only. Not investment advice. "
           "Data may be delayed. Past performance does not guarantee future results.")