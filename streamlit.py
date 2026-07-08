import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("NIFTY 50 Risk-Adjusted Performance Metrics")

#SIDEBAR

st.sidebar.header("Settings")

ticker = st.sidebar.text_input("Enter Ticker Symbol", "AAPL")

window_size = st.sidebar.number_input("Enter Rolling Window Size (in days)", min_value = 1, max_value = 756, value = 252, step = 1)


date_range = st.sidebar.date_input("Select Date Range", 
                                   value=(pd.to_datetime("2015-01-01"), pd.to_datetime("2026-01-01")))


metric_options = ["Equity", "Sharpe", "Sortino", "Calmar", "Drawdown"]
selected_metrics = st.sidebar.multiselect("Select Metrics to Display",
                       options=metric_options,
                       default=metric_options[0])

st.sidebar.subheader("Comparison Mode")

comparison_options = ["SPY", "QQQ", "NVDA", "BTC-USD", "AAPL"]

comparison_tickers = st.sidebar.multiselect(
    "Compare against",
    options=comparison_options,
    default=[]
)

st.sidebar.write("Show")
show_sharpe_comp = st.sidebar.checkbox("Sharpe comparison", value=True)
show_drawdown_comp = st.sidebar.checkbox("Drawdown comparison", value=True)
show_equity_comp = st.sidebar.checkbox("Equity comparison", value=True)

st.sidebar.subheader("Additional Options")
show_heatmap = st.sidebar.checkbox("Sharpe heatmap by year", value=True)



# main body

st.write(f"Selected Ticker: {ticker}")
st.write("Window Size (in days):", window_size)
st.write("Selected Date Range:", date_range[0], "to", date_range[1])


# Cache:

@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)

    if data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        close = data['Close'][ticker]
    else:
        close = data['Close']

    return close

@st.cache_data
def compute_metrics(close, window_size):
    returns = close.pct_change().dropna()
    
    rolling_mean = returns.rolling(window=window_size).mean()
    rolling_std = returns.rolling(window=window_size).std()
    sharpe_ratio = ((rolling_mean / rolling_std) * np.sqrt(252)).dropna()
    
    equity = (1 + returns).cumprod()
    
    negative_returns = returns.copy()
    negative_returns[negative_returns > 0] = 0
    downside_std = negative_returns.rolling(window_size).std()
    sortino_ratio = ((rolling_mean / downside_std) * np.sqrt(252)).dropna()
    
    running_max = equity.cummax()
    full_drawdown = (equity / running_max - 1)
    
    start_val = equity.shift(window_size - 1)
    rolling_peak = equity.rolling(window_size).max()
    drawdown = equity / rolling_peak - 1
    rolling_drawdown = drawdown.rolling(window_size).min().dropna()
    cagr = (equity / start_val) - 1
    calmar_ratio = (cagr / rolling_drawdown.abs()).dropna()
    
    return {
        "returns": returns,
        "equity": equity,
        "sharpe": sharpe_ratio,
        "sortino": sortino_ratio,
        "calmar": calmar_ratio,
        "drawdown": full_drawdown,
        "rolling_drawdown": rolling_drawdown,
    }

if load_data(ticker, date_range[0], date_range[1]) is None:
    st.error(f"No data found for ticker '{ticker}' in the selected date range. Please check the ticker symbol and date range.")
    st.stop()

if len(date_range) != 2:
    st.stop()




# CALCULATIONS PANEL

start_date, end_date = date_range

comparison_data = {}

for comp_ticker in comparison_tickers:
    comp_close = load_data(comp_ticker, start_date, end_date)
    
    if comp_close is None or comp_close.empty:
        st.warning(f"No data found for comparison ticker '{comp_ticker}' — skipping.")
        continue
    
    comparison_data[comp_ticker] = compute_metrics(comp_close, window_size)

close = load_data(ticker, start_date, end_date)

computed_metrics = compute_metrics(close, window_size)

def yearly_avg_heatmap_data(series):
    yearly_avg = series.groupby(series.index.year).mean()
    return yearly_avg

n_days = len(computed_metrics["returns"])
annual_return = (computed_metrics["equity"].iloc[-1] / computed_metrics["equity"].iloc[0]) ** (252 / n_days) - 1
volatility = computed_metrics["returns"].std() * np.sqrt(252)

running_max = computed_metrics["equity"].cummax()
full_drawdown = computed_metrics["equity"] / running_max - 1
current_drawdown = full_drawdown.iloc[-1]
worst_drawdown = full_drawdown.min()

# ANALYTICS PANEL 

st.subheader(f"Latest snapshot — {ticker}")

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7 = st.columns(3)

with col1:
    st.metric("Annual Return", f"{annual_return:.1%}")

with col2:
    st.metric("Volatility", f"{volatility:.1%}")

with col3:
    st.metric("Sharpe", f"{computed_metrics['sharpe'].iloc[-1]:.2f}" if not computed_metrics['sharpe'].empty else "N/A")

with col4:
    st.metric("Sortino", f"{computed_metrics['sortino'].iloc[-1]:.2f}" if not computed_metrics['sortino'].empty else "N/A")

with col5:
    st.metric("Current Drawdown", f"{current_drawdown:.1%}")

with col6:
    st.metric("Worst Drawdown", f"{worst_drawdown:.1%}")

with col7:
    st.metric("Current Calmar", f"{computed_metrics['calmar'].iloc[-1]:.2f}" if not computed_metrics['calmar'].empty else "N/A")


print(yearly_avg_heatmap_data(computed_metrics["sharpe"]).head())

if show_heatmap:
    st.header("Sharpe Ratio Heatmap by Year")
    yearly_sharpe = yearly_avg_heatmap_data(computed_metrics["sharpe"])

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=[[val] for val in yearly_sharpe.values],
        x=["Avg Sharpe"],
        y=[str(year) for year in yearly_sharpe.index],
        colorscale="Inferno",
        text=[[f"{val:.6f}"] for val in yearly_sharpe.values],
        texttemplate="%{text}",
        showscale=True
    ))

    fig_heatmap.update_yaxes(title_text="Year")

    fig_heatmap.update_layout(
        yaxis=dict(autorange="reversed"),  # so earliest year is on top
        height=400
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# MAIN PANEL

if "Equity" in selected_metrics:
    st.header("Equity Curve")
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(x=computed_metrics['equity'].index, y=computed_metrics['equity'], name = f"{ticker}", line=dict(color='blue')))
    fig_equity.update_layout(
    xaxis=dict(title="Date"),
    yaxis=dict(title="Equity")
)
    if show_equity_comp:
        for comp_ticker, comp_metrics in comparison_data.items():
            fig_equity.add_trace(go.Scatter(
                x=comp_metrics["equity"].index, 
                y=comp_metrics["equity"], 
                name=comp_ticker
            ))

    st.plotly_chart(fig_equity, use_container_width=True)


if "Sharpe" in selected_metrics:
    st.header("Sharpe Ratio")
    fig_sharpe = go.Figure()
    fig_sharpe.add_trace(go.Scatter(x=computed_metrics['sharpe'].index, y=computed_metrics['sharpe'], name = f"{ticker}", line=dict(color='green')))
    fig_sharpe.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Sharpe Ratio")
    )

    if show_sharpe_comp:
        for comp_ticker, comp_metrics in comparison_data.items():
            fig_sharpe.add_trace(go.Scatter(
                x=comp_metrics["sharpe"].index, 
                y=comp_metrics["sharpe"], 
                name=comp_ticker
            ))

    st.plotly_chart(fig_sharpe, use_container_width=True)


if "Sortino" in selected_metrics:
    st.header("Sortino Ratio")
    fig_sortino = go.Figure()
    fig_sortino.add_trace(go.Scatter(x=computed_metrics['sortino'].index, y=computed_metrics['sortino'], name=f"{ticker}", line=dict(color='cyan')))
    fig_sortino.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Sortino Ratio")
    )


    st.plotly_chart(fig_sortino, use_container_width=True)

if "Calmar" in selected_metrics:
    st.header("Calmar Ratio")
    fig_calmar = go.Figure()
    fig_calmar.add_trace(go.Scatter(x=computed_metrics['calmar'].index, y=computed_metrics['calmar'], name=f"{ticker}", line=dict(color='magenta')))
    fig_calmar.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Calmar Ratio")
    )
    st.plotly_chart(fig_calmar, use_container_width=True)

if "Drawdown" in selected_metrics:
    st.header("Full Drawdown")
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(x=full_drawdown.index, y=full_drawdown, name=f"{ticker}", line=dict(color='red')))
    fig_dd.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Drawdown")
    )

    if show_drawdown_comp:
        for comp_ticker, comp_metrics in comparison_data.items():
            fig_dd.add_trace(go.Scatter(
                x=comp_metrics["drawdown"].index,
                y=comp_metrics["drawdown"],
                name=comp_ticker
            ))
    
    st.plotly_chart(fig_dd, use_container_width=True)

    