import operator
import pandas as pd
import streamlit as st

from data import get_many
from indicators import INDICATORS, compute, label
from stocks import NIFTY_LARGE

st.set_page_config(page_title="Screener", page_icon="🔍", layout="wide")
st.title("🔍 Stock Screener")
st.caption("Indicator chuno, uski settings apne hisaab se badlo, aur conditions jodo. "
           "Sab conditions ek saath sahi honi chahiye (AND).")

OPS = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le}


@st.cache_data(ttl=600)
def load_data():
    return get_many(NIFTY_LARGE)


def picker(prefix, default="RSI"):
    """Indicator + uski settings user se leta hai."""
    names = list(INDICATORS)
    name = st.selectbox("Indicator", names, index=names.index(default), key=f"{prefix}_ind")
    spec = INDICATORS[name]["params"]
    params = {}
    if spec:
        cols = st.columns(len(spec))
        for col, (p, cfg) in zip(cols, spec.items()):
            key = f"{prefix}_{name}_{p}"
            if "options" in cfg:
                params[p] = col.selectbox(p, cfg["options"], key=key)
            elif isinstance(cfg["default"], float):
                params[p] = col.number_input(p, min_value=float(cfg["min"]),
                                             max_value=float(cfg["max"]),
                                             value=float(cfg["default"]), step=0.1, key=key)
            else:
                params[p] = col.number_input(p, min_value=int(cfg["min"]),
                                             max_value=int(cfg["max"]),
                                             value=int(cfg["default"]), step=1, key=key)
    ago = st.number_input("Kitne din pehle ki value? (0 = aaj)", min_value=0, max_value=60,
                          value=0, step=1, key=f"{prefix}_ago")
    st.caption(f"ℹ️ {INDICATORS[name]['help']}")
    return name, params, int(ago)


data = load_data()
symbols = list(data.keys())

if "n_cond" not in st.session_state:
    st.session_state.n_cond = 1

b1, b2, _ = st.columns([1, 1, 6])
if b1.button("➕ Condition"):
    st.session_state.n_cond += 1
if b2.button("➖ Hatao") and st.session_state.n_cond > 1:
    st.session_state.n_cond -= 1

mask = pd.Series(True, index=symbols)
out = {"Price": pd.Series({s: float(data[s]["Close"].iloc[-1]) for s in symbols})}

for i in range(st.session_state.n_cond):
    with st.container(border=True):
        st.markdown(f"**Condition {i + 1}**")
        left = picker(f"L{i}", "RSI")
        c1, c2 = st.columns([1, 2])
        op = c1.selectbox("Condition", list(OPS), index=1, key=f"op{i}")
        mode = c2.radio("Compare with", ["Number", "Indicator"], horizontal=True, key=f"mode{i}")

        left_vals = pd.Series({s: compute(data[s], *left) for s in symbols})
        out[label(*left)] = left_vals

        if mode == "Number":
            right_vals = st.number_input("Value", value=30.0, key=f"val{i}")
        else:
            right = picker(f"R{i}", "SMA")
            right_vals = pd.Series({s: compute(data[s], *right) for s in symbols})
            out[label(*right)] = right_vals

    mask &= OPS[op](left_vals, right_vals)

table = pd.DataFrame(out).round(2)
table.index.name = "Symbol"
result = table[mask].reset_index()

st.subheader(f"{len(result)} stocks match (total {len(symbols)} scan hue)")
st.dataframe(result, hide_index=True, width="stretch")

st.divider()
st.caption("For educational purposes only. Not investment advice. "
           "Data may be delayed. Past performance does not guarantee future results.")