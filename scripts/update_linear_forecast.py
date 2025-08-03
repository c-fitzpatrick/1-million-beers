#!/usr/bin/env python3
"""
Script to update linear forecast by running    # Create initial plot with outliers highlighted
    fig1 = plot_beer_counts(chat_df, color='error')
    fig1.write_html("beer_counts_with_outliers.html")
    fig1.write_image("beer_counts_with_outliers.png", width=1200, height=800, scale=2) contents of parse_whatsapp_chat.ipynb
This script:
1. Dynamically finds the most recent WhatsApp chat file from the bucket
2. Processes the data and creates forecasts 
3. Saves plots as PNG files
4. Saves forecast content to content_forecast.txt
"""

import pandas as pd
import re
import math
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
import os
import sys
from datetime import datetime
from google.cloud import storage

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from src.plotting import plot_beer_counts, estimate_time_to_million_beers
from src.data_cleaning import import_and_clean_chat

from dotenv import load_dotenv
load_dotenv()


def get_most_recent_chat_file(bucket_name='1-million-beers'):
    """
    Get the most recently updated WhatsApp chat file from the Google Cloud Storage bucket.
    
    Args:
        bucket_name (str): Name of the Google Cloud Storage bucket
        
    Returns:
        str: Name of the most recent file
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # List all blobs that match the WhatsApp chat pattern
    blobs = list(bucket.list_blobs(prefix="WhatsApp Chat with 1 Million Beers"))
    
    if not blobs:
        raise ValueError("No WhatsApp chat files found in bucket")
    
    # Sort by time_created (most recent first)
    most_recent_blob = max(blobs, key=lambda blob: blob.time_created)
    
    return most_recent_blob.name


def main():
    """
    Main function that replicates the notebook functionality.
    """
    print("Starting linear forecast update...")
    
    # Get the most recent chat file
    file_path = get_most_recent_chat_file()
    
    # Import and clean the chat data
    chat_df = import_and_clean_chat(file_path)
    
    # Create initial plot with outliers highlighted
    fig1 = plot_beer_counts(chat_df, color='error')
    fig1.write_image("beer_counts_with_outliers.png", width=1200, height=800, scale=2)
    fig1.write_html("beer_counts_with_outliers.html")
    
    # Manual outlier removal (replicating notebook cell)
    chat_df = chat_df[chat_df['datetime'] != pd.Timestamp('2025-06-14 17:43:00')]
    chat_df = chat_df[chat_df['datetime'] != pd.Timestamp('2025-06-19 23:45:00')]
    
    # Linear regression analysis
    data_cleaned = chat_df[chat_df['error'] == 'none'].copy()
    
    # Prepare X as hours since start, y as n_beers
    X = (data_cleaned['hour'] - data_cleaned['hour'].min()).dt.total_seconds().values.reshape(-1, 1) / 3600
    y = data_cleaned['n_beers'].values
    
    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y)
    rate_per_hour = model.coef_[0]
    intercept = model.intercept_
    
    # Add linear estimate to DataFrame for plotting
    data_cleaned.loc[:, 'linear_estimate'] = model.predict(X)
    
    # Create plot with linear forecast
    fig2 = plot_beer_counts(data_cleaned, title='n_beers 🍻 (cleaned outliers) with Linear Forecast')
    
    # Add linear estimate line
    fig2.add_trace(go.Scatter(
        x=data_cleaned['datetime'],
        y=data_cleaned['linear_estimate'],
        mode='lines',
        name='Linear Forecast',
        line=dict(dash='dash')
    ))
    
    # Update legend position and ensure proper date formatting
    fig2.update_layout(
        legend=dict(x=1, y=0, traceorder='normal', xanchor='right', yanchor='bottom'),
        xaxis=dict(
            tickformat='%Y-%m-%d',
            tickangle=45,
            showgrid=True,
            gridcolor='lightgray'
        )
    )
    fig2.write_image("beer_counts_with_linear_forecast.png", width=1200, height=800, scale=2)
    fig2.write_html("beer_counts_with_linear_forecast.html")

    # Calculate forecasts
    # Next round 10k
    start = data_cleaned['n_beers'].max()
    next_10k = math.ceil(start / 10000) * 10000
    rate_per_hour_10k, days_needed_10k, years_needed_10k, date_estimate_10k, start_10k, target_10k = estimate_time_to_million_beers(data_cleaned, rate_per_hour, next_10k)
    
    forecast_10k = f"At a rate of {rate_per_hour_10k:.2f} beers/hour, it will take approximately {days_needed_10k:.1f} days to go from {start_10k:,.0f} to {target_10k:,} beers."
    
    # Target 1,000,000
    rate_per_hour_1m, days_needed_1m, years_needed_1m, date_estimate_1m, start_1m, target_1m = estimate_time_to_million_beers(data_cleaned, rate_per_hour)
    
    forecast_1m = f"At a rate of {rate_per_hour_1m:.2f} beers/hour, it will take approximately {years_needed_1m:.1f} years ({date_estimate_1m.date()}) to reach {target_1m:,} beers (from {start_1m:,.0f})."
    
    # Save forecast content to text file
    content = f"""Linear Forecast Update
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source file: {file_path}

Data Summary:
- Total messages processed: {len(chat_df)}
- Clean data points: {len(data_cleaned)}
- Current beer count: {start:,.0f}
- Rate per hour: {rate_per_hour:.2f} beers/hour
- Model intercept: {intercept:.2f}

Forecasts:

Next 10k milestone ({target_10k:,} beers):
{forecast_10k}

One Million Beers Goal:
{forecast_1m}
"""
    
    with open('content_forecast.txt', 'w') as f:
        f.write(content)
    
    print("Linear forecast update completed successfully!")


if __name__ == "__main__":
    main()