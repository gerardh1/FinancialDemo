"""
Stock Price Dashboard
=====================
A Streamlit dashboard for viewing stock prices and technical indicators.

Usage: streamlit run app.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =============================================================================
# CONFIGURATION
# =============================================================================

API_KEY = "SFJafufqIR0Yh8WjC6QWqENdCYTontMg"
BASE_URL = "https://financialmodelingprep.com"


# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

@st.cache_data(ttl=60)
def get_quote(symbol: str) -> dict | None:
    """
    Fetch current stock quote data.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        Quote data dictionary or None if request fails
    """
    url = f"{BASE_URL}/stable/quote?symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    return None


@st.cache_data(ttl=300)
def get_historical(symbol: str) -> pd.DataFrame:
    """
    Fetch historical price data for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        DataFrame with historical OHLCV data
    """
    url = f"{BASE_URL}/api/v3/historical-price-full/{symbol}?apikey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "historical" in data:
            df = pd.DataFrame(data["historical"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            return df
    
    return pd.DataFrame()


# =============================================================================
# CHART FUNCTIONS
# =============================================================================

def create_candlestick_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a candlestick chart with volume subplot.
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        Plotly Figure object
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Volume bars with color based on price direction
    colors = [
        "red" if df["close"].iloc[i] < df["open"].iloc[i] else "green"
        for i in range(len(df))
    ]
    
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["volume"],
            marker_color=colors,
            name="Volume"
        ),
        row=2, col=1
    )
    
    # Layout settings
    fig.update_layout(
        template="simple_white",
        xaxis_rangeslider_visible=False,
        height=600,
        showlegend=False
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig


def create_moving_average_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart with moving averages.
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        Plotly Figure object
    """
    # Calculate moving averages
    df = df.copy()
    df["MA20"] = df["close"].rolling(window=20).mean()
    df["MA50"] = df["close"].rolling(window=50).mean()
    
    fig = go.Figure()
    
    # Close price line
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["close"],
            mode="lines",
            name="Close",
            line=dict(color="blue")
        )
    )
    
    # 20-day MA
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["MA20"],
            mode="lines",
            name="MA20",
            line=dict(dash="dash", color="orange")
        )
    )
    
    # 50-day MA
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["MA50"],
            mode="lines",
            name="MA50",
            line=dict(dash="dot", color="red")
        )
    )
    
    fig.update_layout(
        template="simple_white",
        height=400,
        yaxis_title="Price (USD)"
    )
    
    return fig


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def display_metrics(quote_data: dict):
    """Display stock metrics in a grid layout."""
    q = quote_data
    
    # Row 1: Price metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Price",
        f"${q.get('price', 0):.2f}",
        f"{q.get('changesPercentage', 0):.2f}%"
    )
    col2.metric("Day High", f"${q.get('dayHigh', 0):.2f}")
    col3.metric("Day Low", f"${q.get('dayLow', 0):.2f}")
    col4.metric("Volume", f"{q.get('volume', 0):,}")
    
    # Row 2: Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("52-Week High", f"${q.get('yearHigh', 0):.2f}")
    col6.metric("52-Week Low", f"${q.get('yearLow', 0):.2f}")
    col7.metric("Market Cap", f"${q.get('marketCap', 0) / 1e9:.2f}B")
    col8.metric("P/E Ratio", f"{q.get('pe', 'N/A')}")


def display_charts(ticker: str, historical: pd.DataFrame):
    """Display historical charts and data table."""
    st.subheader(f"{ticker} - Historical Price")
    
    # Filter to last 6 months (180 trading days)
    last_6m = historical.tail(180)
    
    # Candlestick chart
    candlestick_fig = create_candlestick_chart(last_6m)
    st.plotly_chart(candlestick_fig, use_container_width=True)
    
    # Moving averages chart
    st.subheader("Moving Averages")
    ma_fig = create_moving_average_chart(last_6m)
    st.plotly_chart(ma_fig, use_container_width=True)
    
    # Recent data table
    st.subheader("Recent Data")
    display_cols = ["date", "open", "high", "low", "close", "volume"]
    st.dataframe(
        last_6m.tail(10)[display_cols],
        use_container_width=True
    )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(page_title="Stock Dashboard", layout="wide")
    
    # Header
    st.title("📈 Stock Price Dashboard")
    st.caption("Data source: Financial Modeling Prep API")
    
    # Sidebar
    st.sidebar.header("Settings")
    ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")
    
    # Fetch data
    quote = get_quote(ticker)
    historical = get_historical(ticker)
    
    # Display content
    if quote and len(quote) > 0:
        display_metrics(quote[0])
        st.divider()
        
        if not historical.empty:
            display_charts(ticker, historical)
    else:
        st.error("Could not fetch data. Please check the ticker symbol.")


if __name__ == "__main__":
    main()