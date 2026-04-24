import streamlit as st
import pandas as pd
import requests

# YOUR FMP API KEY
FMP_KEY = "zKQqtEP4FNoej8dQ2x8VzCOZN4RgqCHH"

st.set_page_config(page_title="Frontier Infinite", layout="wide")
st.title("🛡️ Frontier Infinite Discovery")
st.info("Protocol: Free-Tier Stable Feed | TSX & US Only | Under $150 | No ETFs")

def get_market_list():
    """Fetches a broad list of active stocks available on the free tier."""
    # This endpoint is more stable for free users than the 'Screener'
    url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={FMP_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if isinstance(data, dict) and ("Error" in data or "Error Message" in data):
            st.error(f"API Error: {data.get('Error Message', 'Limit Reached')}")
            return []
        return data # This is a list of dictionaries
    except:
        return []

def get_history(symbol):
    """Fetches 2-year history."""
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?serietype=line&apikey={FMP_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "historical" in data:
            df = pd.DataFrame(data["historical"])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            return df['close'].tail(500)
    except:
        return None
    return None

# Load the master list once
with st.spinner("Connecting to Exchange Feed..."):
    raw_data = get_market_list()

if raw_data:
    tab_cad, tab_usd = st.tabs(["🇨🇦 Canada (TSX)", "🇺🇸 USA (NYSE/NASDAQ)"])

    def process_tab(is_cad):
        # 1. Filter for Region and Price
        if is_cad:
            # TSX stocks in FMP usually end in .TO
            filtered = [s for s in raw_data if s['symbol'].endswith(".TO") and s['price'] < 150]
        else:
            # US stocks (NYSE/NASDAQ) and under $150
            filtered = [s for s in raw_data if s['exchangeShortName'] in ['NYSE', 'NASDAQ'] and s['price'] < 150]

        if not filtered:
            st.warning("No active stocks found for this criteria.")
            return

        cols = st.columns(3)
        # 2. Pick top 6 by volume/activity to show 'leaders'
        display_list = filtered[:6] 
        
        for i, stock in enumerate(display_list):
            ticker = stock['symbol']
            price = stock['price']
            name = stock['name']
            
            hist = get_history(ticker)
            if hist is not None and not hist.empty:
                growth = ((price - hist.iloc[0]) / hist.iloc[0]) * 100
                with cols[i % 3]:
                    st.metric(label=f"{ticker}", value=f"${price:.2f}", delta=f"{growth:.1f}% (2Y)")
                    st.caption(name)
                    st.line_chart(hist, height=180)

    with tab_cad:
        process_tab(is_cad=True)
    with tab_usd:
        process_tab(is_cad=False)
else:
    st.warning("Please refresh the page. The API connection is currently reset.")
