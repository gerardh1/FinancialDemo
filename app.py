# ============================================================================
# STREAMLIT + PLOTLY FINANCE DASHBOARD (Financial Modeling Prep API)
# ============================================================================
# Save this code as "app.py" and run with: streamlit run app.py
# ============================================================================
 
streamlit_code = '''
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# API Key
API_KEY = "SFJafufqIR0Yh8WjC6QWqENdCYTontMg"

# Page config
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# Title
st.title("📈 Stock Price Dashboard")
st.caption("Data source: Financial Modeling Prep API")

# Sidebar for user input
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")

# Fetch quote data
@st.cache_data(ttl=60)
def get_quote(symbol):
    url = f"https://financialmodelingprep.com/stable/quote?symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Fetch historical data
@st.cache_data(ttl=300)
def get_historical(symbol):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "historical" in data:
            df = pd.DataFrame(data["historical"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            return df
    return pd.DataFrame()

# Get data
quote = get_quote(ticker)
historical = get_historical(ticker)

if quote and len(quote) > 0:
    q = quote[0]
    
    # Display current metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Price", f"${q.get('price', 0):.2f}", f"{q.get('changesPercentage', 0):.2f}%")
    col2.metric("Day High", f"${q.get('dayHigh', 0):.2f}")
    col3.metric("Day Low", f"${q.get('dayLow', 0):.2f}")
    col4.metric("Volume", f"{q.get('volume', 0):,}")
    
    # More metrics
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("52-Week High", f"${q.get('yearHigh', 0):.2f}")
    col6.metric("52-Week Low", f"${q.get('yearLow', 0):.2f}")
    col7.metric("Market Cap", f"${q.get('marketCap', 0)/1e9:.2f}B")
    col8.metric("P/E Ratio", f"{q.get('pe', 'N/A')}")
    
    st.divider()
    
    # Historical chart
    if not historical.empty:
        st.subheader(f"{ticker} - Historical Price")
        
        # Filter last 6 months
        last_6m = historical.tail(180)
        
        # Create candlestick with volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=last_6m["date"],
                open=last_6m["open"],
                high=last_6m["high"],
                low=last_6m["low"],
                close=last_6m["close"],
                name="Price"
            ),
            row=1, col=1
        )
        
        # Volume bars
        colors = ["red" if last_6m["close"].iloc[i] < last_6m["open"].iloc[i] else "green" 
                  for i in range(len(last_6m))]
        fig.add_trace(
            go.Bar(x=last_6m["date"], y=last_6m["volume"], marker_color=colors, name="Volume"),
            row=2, col=1
        )
        
        fig.update_layout(
            template="simple_white",
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=False
        )
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Moving Averages Chart
        st.subheader("Moving Averages")
        last_6m["MA20"] = last_6m["close"].rolling(window=20).mean()
        last_6m["MA50"] = last_6m["close"].rolling(window=50).mean()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=last_6m["date"], y=last_6m["close"], mode="lines", name="Close"))
        fig2.add_trace(go.Scatter(x=last_6m["date"], y=last_6m["MA20"], mode="lines", name="MA20", line=dict(dash="dash")))
        fig2.add_trace(go.Scatter(x=last_6m["date"], y=last_6m["MA50"], mode="lines", name="MA50", line=dict(dash="dot")))
        fig2.update_layout(template="simple_white", height=400, yaxis_title="Price (USD)")
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Data table
        st.subheader("Recent Data")
        st.dataframe(last_6m.tail(10)[["date", "open", "high", "low", "close", "volume"]], use_container_width=True)
else:
    st.error("Could not fetch data. Please check the ticker symbol.")
'''

print(streamlit_code)
print("\n" + "="*60)
print("To run this dashboard:")
print("1. Save the code above to a file named 'app.py'")
print("2. Install required packages: pip install streamlit requests plotly")
print("3. Run: streamlit run app.py")
print("="*60)