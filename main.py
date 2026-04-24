import streamlit as st
import pandas as pd
import requests

# YOUR FMP API KEY
FMP_KEY = "zKQqtEP4FNoej8dQ2x8VzCOZN4RgqCHH"

st.set_page_config(page_title="Frontier Infinite", layout="wide")
st.title("🛡️ Frontier Infinite Discovery")
st.info("Status: Live FMP Feed | TSX & US Only | Under $150 | Zero Hard-Coded Lists")

def get_dynamic_leaders(is_cad):
    """Uses FMP Screener to find the 10 most active stocks meeting your criteria."""
    exchange = 'TSX' if is_cad else 'NYSE,NASDAQ'
    # Pure discovery: price < 150, not an ETF, on specific exchange
    url = f"https://financialmodelingprep.com/api/v3/stock-screener?priceLowerThan=150&isEtf=false&exchange={exchange}&limit=10&apikey={FMP_KEY}"
    try:
        r = requests.get(url)
        return r.json()
    except:
        return []

def get_history(symbol):
    """Fetches clean historical data for the 2-year 'Staircase' view."""
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?serietype=line&apikey={FMP_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "historical" in data:
            df = pd.DataFrame(data["historical"])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            # Return last 500 trading days (~2 years)
            return df['close'].tail(500)
    except:
        return None
    return None

tab_cad, tab_usd = st.tabs(["🇨🇦 Canadian Discovery (TSX)", "🇺🇸 US Discovery (NYSE/NASDAQ)"])

def render_market(is_cad):
    with st.spinner(f"Scanning {'TSX' if is_cad else 'US'} Market..."):
        leaders = get_dynamic_leaders(is_cad)
        
    if not leaders:
        st.warning("No active leads found. Please check your FMP quota or connection.")
        return

    cols = st.columns(3)
    display_count = 0
    
    for stock in leaders:
        if display_count >= 6: break # Show top 6 most active
        
        ticker = stock['symbol']
        price = stock['price']
        name = stock['companyName']
        
        hist = get_history(ticker)
        if hist is not None and not hist.empty:
            # Calculate 2-Year Growth
            growth = ((price - hist.iloc[0]) / hist.iloc[0]) * 100
            
            with cols[display_count % 3]:
                st.metric(label=f"{ticker} ({name})", 
                          value=f"${price:.2f}", 
                          delta=f"{growth:.1f}% (2Y)")
                st.line_chart(hist, height=180)
                display_count += 1

with tab_cad:
    render_market(is_cad=True)

with tab_usd:
    render_market(is_cad=False)
