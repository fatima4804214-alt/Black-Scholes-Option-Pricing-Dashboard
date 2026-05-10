import streamlit as st
try:
    import yfinance as yf
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "yfinance"], check=True)
    import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from black_scholes import black_scholes
from volatility import calculate_volatility

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Black-Scholes Dashboard",
    page_icon="📈",
    layout="wide"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .main { background-color: #0f0f0f; }
    
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #666;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 28px;
        font-weight: 600;
        color: #f0f0f0;
    }
    .call-value { color: #4ade80; }
    .put-value  { color: #f87171; }
    .vol-value  { color: #facc15; }

    .section-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 3px;
        color: #555;
        text-transform: uppercase;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #222;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #1e1e1e;
        font-size: 13px;
    }
    .info-key   { color: #666; font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
    .info-val   { color: #ccc; font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
    .stButton > button {
        background: #f0f0f0 !important;
        color: #0f0f0f !important;
        border: none !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 1px !important;
        padding: 10px 32px !important;
        border-radius: 4px !important;
        width: 100%;
    }
    .stButton > button:hover { background: #d0d0d0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("## 📈 Black-Scholes Option Pricing Dashboard")
st.markdown("<p style='color:#555; font-family:IBM Plex Mono,monospace; font-size:12px; letter-spacing:2px;'>LIVE MARKET DATA  ·  OPTIONS PRICING  ·  VOLATILITY ANALYSIS</p>", unsafe_allow_html=True)
st.markdown("---")

# ─── SIDEBAR INPUTS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Parameters")
    st.markdown("<div class='section-title'>Stock</div>", unsafe_allow_html=True)
    
    symbol = st.text_input("Stock Symbol", value="AAPL", placeholder="e.g. AAPL, TSLA, GOOGL").upper().strip()
    
    st.markdown("<div class='section-title' style='margin-top:20px;'>Option Inputs</div>", unsafe_allow_html=True)
    
    K = st.number_input("Strike Price (K)", min_value=1.0, value=150.0, step=1.0,
                        help="The price at which you can buy/sell the stock")
    T = st.number_input("Time to Expiry (years)", min_value=0.01, max_value=5.0, value=0.25, step=0.05,
                        help="0.25 = 3 months, 0.5 = 6 months, 1.0 = 1 year")
    r = st.number_input("Risk-Free Rate", min_value=0.0, max_value=0.2, value=0.05, step=0.005,
                        format="%.3f", help="US Treasury rate (default 5%)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("▶  CALCULATE", use_container_width=True)

# ─── MAIN LOGIC ──────────────────────────────────────────────────────────────
if run:
    with st.spinner(f"Fetching live data for {symbol}..."):
        try:
            raw = yf.download(symbol, period="6mo", interval="1d", progress=False)
            
            if raw.empty:
                st.error(f"No data found for symbol **{symbol}**. Please check the ticker.")
                st.stop()

            # Fix MultiIndex if present
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            
            data = raw.reset_index().dropna()
            
            # Flatten any remaining column issues
            data.columns = [str(c) for c in data.columns]

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.stop()

    # ── Calculations ──
    sigma = calculate_volatility(data)
    S     = float(data['Close'].iloc[-1])

    call_price, d1, d2 = black_scholes(S, K, T, r, sigma, 'call')
    put_price,  _,  _  = black_scholes(S, K, T, r, sigma, 'put')

    # ── Top Metrics ──
    st.markdown("<div class='section-title'>Results</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Current Price</div>
            <div class='metric-value'>${S:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Call Option Price</div>
            <div class='metric-value call-value'>${call_price:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Put Option Price</div>
            <div class='metric-value put-value'>${put_price:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Annualized Volatility</div>
            <div class='metric-value vol-value'>{sigma*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart + Parameters side by side ──
    col_chart, col_params = st.columns([3, 1])

    with col_chart:
        st.markdown("<div class='section-title'>6-Month Price History</div>", unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(11, 4.5))
        fig.patch.set_facecolor('#111111')
        ax.set_facecolor('#111111')

        dates  = pd.to_datetime(data['Date'])
        closes = data['Close'].astype(float)

        ax.plot(dates, closes, color='#e0e0e0', linewidth=1.5, label=f'{symbol} Close')
        ax.fill_between(dates, closes, closes.min(), alpha=0.08, color='#e0e0e0')
        ax.axhline(S, color='#4ade80', linestyle='--', linewidth=1, alpha=0.7, label=f'Last: ${S:.2f}')
        ax.axhline(K, color='#facc15', linestyle=':', linewidth=1, alpha=0.7, label=f'Strike: ${K:.2f}')

        mid_date = dates.iloc[len(dates)//2]
        ax.annotate(f'CALL  ${call_price:.2f}', xy=(mid_date, S),
                    xytext=(mid_date, S * 1.03),
                    color='#4ade80', fontsize=9, fontfamily='monospace',
                    arrowprops=dict(arrowstyle='->', color='#4ade80', lw=0.8))
        ax.annotate(f'PUT   ${put_price:.2f}', xy=(mid_date, S),
                    xytext=(mid_date, S * 0.94),
                    color='#f87171', fontsize=9, fontfamily='monospace',
                    arrowprops=dict(arrowstyle='->', color='#f87171', lw=0.8))

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=30, color='#555', fontsize=9)
        plt.yticks(color='#555', fontsize=9)
        ax.spines[['top','right','left','bottom']].set_color('#222')
        ax.tick_params(colors='#555')
        ax.yaxis.label.set_color('#555')
        ax.set_ylabel('Price (USD)', color='#555', fontsize=9)
        ax.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor='#aaa', fontsize=9)
        ax.grid(True, color='#1e1e1e', linewidth=0.5)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_params:
        st.markdown("<div class='section-title'>Model Inputs</div>", unsafe_allow_html=True)
        params = {
            "Symbol": symbol,
            "Spot Price (S)": f"${S:.2f}",
            "Strike Price (K)": f"${K:.2f}",
            "Expiry (T)": f"{T:.2f} yr",
            "Risk-Free (r)": f"{r*100:.1f}%",
            "Volatility (σ)": f"{sigma*100:.1f}%",
            "d1": f"{d1:.4f}",
            "d2": f"{d2:.4f}",
        }
        for k, v in params.items():
            st.markdown(f"""
            <div class='info-row'>
                <span class='info-key'>{k}</span>
                <span class='info-val'>{v}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        moneyness = "IN THE MONEY ✅" if S > K else ("AT THE MONEY ➖" if S == K else "OUT OF MONEY ❌")
        color = "#4ade80" if S > K else ("#facc15" if S == K else "#f87171")
        st.markdown(f"<p style='font-family:IBM Plex Mono,monospace; font-size:11px; color:{color}; text-align:center;'>{moneyness}</p>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center; padding: 80px 0; color:#333;'>
        <p style='font-family:IBM Plex Mono,monospace; font-size:14px; letter-spacing:3px;'>
            ENTER PARAMETERS IN SIDEBAR AND CLICK CALCULATE
        </p>
    </div>
    """, unsafe_allow_html=True)
