import pandas as pd
import plotly.express as px
import numpy as np


def plot_beer_counts(chat_df, color=None, color_discrete_sequence=None, title=None):
    """
    Plot the number of beers added over time using a scatter plot.
    Args:
        chat_df (DataFrame): DataFrame containing chat data with 'n_beers', 'date', and 'time' columns.
        color (str): Column name to color points by
        color_discrete_sequence: Color sequence for discrete colors
        title (str): Custom title for the plot
    Returns:
        fig: Plotly figure object
    """
    
    # Scatter plot of number and hour for 'added' rows using plotly

    # Ensure 'datetime' column exists
    plot_df = chat_df.copy()

    fig = px.scatter(
        plot_df,
        x='datetime',
        y='n_beers',
        labels={'hour': 'Hour', 'n_beers': '🍻'},
        title=title or 'Scatter Plot of Beers over time 🍻',
        hover_data=['message', 'n_beers'],
        color=color,
        color_discrete_sequence=color_discrete_sequence
    )
    
    # Add weekend highlighting (Saturday and Sunday)
    import plotly.graph_objects as go
    
    # Get date range from the data
    min_date = plot_df['datetime'].min().date()
    max_date = plot_df['datetime'].max().date()
    
    # Find all weekend dates in the range
    current_date = min_date
    while current_date <= max_date:
        if current_date.weekday() in [5, 6]:  # Saturday=5, Sunday=6
            # Add a vertical rectangle for the entire day
            fig.add_vrect(
                x0=pd.Timestamp(current_date),
                x1=pd.Timestamp(current_date) + pd.Timedelta(days=1),
                fillcolor="rgba(255, 140, 0, 0.2)",  # Transparent burnt orange
                layer="below",
                line_width=0,
            )
        current_date += pd.Timedelta(days=1)
        
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis_title='Time',
        yaxis_title='Number of Beers 🍻',
        yaxis=dict(showgrid=False)
    )
    return fig

def estimate_time_to_million_beers(data_cleaned, rate_per_hour, target=1000000):
    """
    Estimate the time required to reach a target number of beers from the current max.
    Prints days, years, and estimated date to reach the target.
    """
    start = data_cleaned['n_beers'].max()
    end = target
    beers_needed = end - start
    hours_needed = beers_needed / rate_per_hour if rate_per_hour > 0 else np.nan
    days_needed = hours_needed / 24
    years_needed = days_needed / 365
    date_estimate = data_cleaned['datetime'].max() + pd.Timedelta(days=days_needed)
    return rate_per_hour, days_needed, years_needed, date_estimate, start, target