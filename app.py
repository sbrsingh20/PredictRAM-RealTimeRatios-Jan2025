import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import time

# Read data from the additional Excel file with calculated metrics
metrics_file_path = "calculated_stock_metrics_full.xlsx"
metrics_df = pd.read_excel(metrics_file_path)

# Global dictionary to store previous data points for continuous charts
stored_data = {param: {'time': [], 'value': []} for param in
               ['Annualized Alpha (Minute)', 'Annualized Volatility (Minute)', 'Sharpe Ratio (Minute)',
                'Treynor Ratio (Minute)', 'Sortino Ratio (Minute)', 'Maximum Drawdown (Minute)', 
                'R-Squared (Minute)', 'Downside Deviation (Minute)', 'Tracking Error (%) (Minute)', 'VaR (95%) (Minute)']}

# Function to fetch real-time stock data from Yahoo Finance
def fetch_stock_data(stock_symbol):
    """Fetch real-time stock data from Yahoo Finance."""
    stock_data = yf.download(stock_symbol, period="1d", interval="1m", group_by='ticker')
    return stock_data

# Streamlit app layout
st.title("Live Stock Metrics Dashboard")

# Dropdown to select stock
stock_symbol = st.selectbox("Select a Stock", metrics_df['Stock Symbol'].unique())

# Display a placeholder for the graphs (this will be updated every minute)
st.write(f"Displaying real-time metrics for {stock_symbol}")

# Risk parameters to plot
risk_params = [
    'Annualized Alpha (Minute)', 'Annualized Volatility (Minute)', 'Sharpe Ratio (Minute)',
    'Treynor Ratio (Minute)', 'Sortino Ratio (Minute)', 'Maximum Drawdown (Minute)', 
    'R-Squared (Minute)', 'Downside Deviation (Minute)', 'Tracking Error (%) (Minute)', 'VaR (95%) (Minute)'
]

# Define a function to update the graphs
def update_metrics():
    # Fetch real-time stock data (1-minute interval)
    stock_data = fetch_stock_data(stock_symbol)

    # Filter the metrics data for the selected stock symbol
    stock_metrics = metrics_df[metrics_df['Stock Symbol'] == stock_symbol].iloc[0]

    # Time of the current minute
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Collect the current values for the risk parameters
    current_values = {param: stock_metrics[param] for param in risk_params}

    # Create continuous charts for each risk parameter
    figures = {}
    for param in risk_params:
        # Add the current time and value to the stored data
        stored_data[param]['time'].append(current_time)
        stored_data[param]['value'].append(current_values[param])

        # Create a line chart for each parameter
        fig = go.Figure()

        # Add the stored time and value for the parameter to the graph
        fig.add_trace(go.Scatter(
            x=stored_data[param]['time'],
            y=stored_data[param]['value'],
            mode='lines+markers',
            name=f"{param}",
            line=dict(color='blue'),
            marker=dict(size=5)
        ))

        # Update layout with title and axis labels
        fig.update_layout(
            title=f"{param} for {stock_symbol}",
            xaxis_title="Time",
            yaxis_title="Value",
            showlegend=True,
            template="plotly_dark",
        )

        # Store the figure
        figures[param] = fig
    
    return figures

# Display loading spinner while updating
with st.spinner('Loading stock metrics...'):
    figures = update_metrics()
    
# Display each figure
for param in risk_params:
    st.plotly_chart(figures[param])

# Wait for 60 seconds before updating again (use time.sleep in the loop only if needed)
st.time.sleep(60)  # 60 seconds delay for the next iteration
