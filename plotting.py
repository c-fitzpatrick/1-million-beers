import pandas as pd
import plotly.express as px


def plot_beer_counts(chat_df, color=None, color_discrete_sequence=None):
    """
    Plot the number of beers added over time using a scatter plot.
    Args:
        chat_df (DataFrame): DataFrame containing chat data with 'n_beers', 'date', and 'time' columns.
    """
    
    # Scatter plot of number and hour for 'added' rows using plotly

    # Ensure 'datetime' column exists
    plot_df = chat_df.copy()

    fig = px.scatter(
        plot_df,
        x='datetime',
        y='n_beers',
        labels={'hour': 'Hour', 'n_beers': '🍻'},
        title='Scatter Plot of Beers over time 🍻',
        hover_data=['message', 'n_beers'],
        color=color,
        color_discrete_sequence=color_discrete_sequence
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis_title='Time',
        yaxis_title='Number of Beers 🍻'
    )
    fig.show()
