import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots




ticker = "^NSEI"

data = yf.download(ticker, start = "2015-01-01", end = "2026-01-01")

close = data['Close']['^NSEI']

returns = close.pct_change()
returns.dropna(inplace = True)


rolling_mean = returns.rolling(window = 252).mean()

rolling_std = returns.rolling(window = 252).std()



sharpe_ratio = (rolling_mean / rolling_std)*np.sqrt(252)

equity = (1 + returns).cumprod()


sharpe_ratio.dropna(inplace = True)




negative_returns = returns.copy()

negative_returns[negative_returns > 0] = 0


downside_std = (
    negative_returns
    .rolling(252)
    .std()
)


rolling_sortino = (rolling_mean / downside_std)*np.sqrt(252)

window = 252

# Rolling 1-year CAGR (equivalent to simple return since window = 1yr)
start = equity.shift(window - 1)
end = equity
cagr = (end / start) - 1

# Rolling max drawdown over the trailing window
rolling_peak = equity.rolling(window).max() # rolling objects don't have a cummax method
drawdown = equity / rolling_peak - 1
rolling_drawdown = drawdown.rolling(window).min()

# Calmar ratio

calmar = cagr / rolling_drawdown.abs()


calmar.dropna(inplace = True)
rolling_drawdown.dropna(inplace = True)
rolling_sortino.dropna(inplace = True)


plt.figure(figsize=(10,5))
plt.plot(calmar, label = "Calmar Ratio")
plt.plot(rolling_drawdown, label = "Rolling Drawdown")
plt.plot(rolling_sortino, label = "Rolling Sortino Ratio")
plt.plot(sharpe_ratio, label = "Rolling Sharpe Ratio")
plt.title("NIFTY 50 Risk-Adjusted Performance Metrics")
plt.xlabel("Date")
plt.ylabel("Metric Value")
plt.legend()
plt.grid(True)

plt.show()


fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(20, 14), sharex=True)

axes[0].plot(calmar, label="Calmar Ratio", color='tab:blue')
axes[0].set_title("Calmar Ratio")
axes[0].grid(True)

axes[1].plot(rolling_drawdown, label="Rolling Drawdown", color='tab:red')
axes[1].set_title("Rolling Drawdown")
axes[1].grid(True)

axes[2].plot(rolling_sortino, label="Rolling Sortino Ratio", color='tab:green')
axes[2].set_title("Rolling Sortino Ratio")
axes[2].grid(True)

axes[3].plot(sharpe_ratio, label="Rolling Sharpe Ratio", color='tab:purple')
axes[3].set_title("Rolling Sharpe Ratio")
axes[3].grid(True)


axes[4].plot(equity, label="Equity Curve", color='tab:orange')
axes[4].set_title("Equity Curve")
axes[4].grid(True)

axes[4].set_xlabel("Date")

fig.suptitle("NIFTY 50 Risk-Adjusted Performance Metrics", fontsize=14)
plt.tight_layout()
plt.show()








fig = make_subplots(
    rows=5, cols=1,
    shared_xaxes=True,
    subplot_titles=("Calmar Ratio", "Rolling Drawdown", "Rolling Sortino Ratio", "Rolling Sharpe Ratio", "Equity Curve"),
    vertical_spacing=0.05
)

fig.add_trace(go.Scatter(x=calmar.index, y=calmar, name="Calmar Ratio", line=dict(color='blue')), row=1, col=1)
fig.add_trace(go.Scatter(x=rolling_drawdown.index, y=rolling_drawdown, name="Rolling Drawdown", line=dict(color='red')), row=2, col=1)
fig.add_trace(go.Scatter(x=rolling_sortino.index, y=rolling_sortino, name="Rolling Sortino", line=dict(color='green')), row=3, col=1)
fig.add_trace(go.Scatter(x=sharpe_ratio.index, y=sharpe_ratio, name="Rolling Sharpe", line=dict(color='purple')), row=4, col=1)
fig.add_trace(go.Scatter(x=equity.index, y=equity, name="Equity Curve", line=dict(color='orange')), row=5, col=1)

fig.update_layout(
    height=900,
    title_text="NIFTY 50 Risk-Adjusted Performance Metrics",
    showlegend=False  # subplot_titles already label each panel
)

fig.update_xaxes(title_text="Date", row=5, col=1)

fig.show()