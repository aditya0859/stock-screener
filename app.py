import streamlit as st
import plotly.graph_objects as go
from data import get_history

st.set_page_config(page_title="Stock Screener", page_icon="📈", layout="wide")

st.title("📈 Stock Screener")
st.caption("Search any NSE/BSE stock and view its chart.")

col1, col2, col3 = st.columns([2, 1, 1])
symbol = col1.text_input("Stock symbol", "RELIANCE")
exchange = col2.selectbox("Exchange", ["NSE", "BSE"])
period = col3.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)

df = get_history(symbol, exchange, period)

if len(df) < 2:
    st.error("Data nahi mila. Symbol check karo (jaise RELIANCE, TCS, INFY).")
else:
    last = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    change = last - prev
    pct = change / prev * 100

    st.metric(f"{symbol.upper()} last close", f"₹{last:,.2f}",
              f"{change:+.2f} ({pct:+.2f}%)")

    fig = go.Figure(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width="Stretch")

    st.subheader("Recent prices")
    st.dataframe(df.tail(10).round(2))

st.divider()
st.caption("For educational purposes only. Not investment advice. "
           "Data may be delayed. Past performance does not guarantee future results.")