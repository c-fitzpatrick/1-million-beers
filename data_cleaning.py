import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from whatsapp_parser import load_whatsapp_chat_from_bucket, parse_chat_lines, process_chat_data

pd.set_option('future.no_silent_downcasting', True)

def beer_errors(chat_df):
    """
    Flag rows with errors in beer counts.
    """
    # Remove rows where n_beers is less than the previous row's n_beers
    chat_df.loc[:,'error_low'] = chat_df['n_beers'] <= chat_df['n_beers'].rolling(window=10).median() -10

    # Remove rows where n_beers greater than row after it
    chat_df.loc[:,'error_high'] = chat_df['n_beers'] >= chat_df['n_beers'].rolling(window=10).median().shift(-10) +10

    return chat_df


def flag_outliers(chat_df):
    """
    Flag outliers in the chat data based on a linear regression model.
    Outliers are defined as points that are more than 3 standard deviations away from the trend line.
        """
    outlier_df = chat_df.copy()
    outlier_df = outlier_df[(outlier_df['error_high'] == False) & (outlier_df['error_low'] == False)]
    # Fit linear regression to hour vs n_beers
    X = (outlier_df['hour'] - outlier_df['hour'].min()).dt.total_seconds().values.reshape(-1, 1) / 3600  # hours since start
    y = outlier_df['n_beers'].values
    model = LinearRegression()
    model.fit(X, y)
    pred = model.predict(X)
    residuals = y - pred
    std_resid = np.std(residuals)

    # Keep only points within 3 standard deviations of the trend
    # added_df_no_outliers = chat_df[np.abs(residuals) <= 3 * std_resid]
    outliers = pd.Series(np.abs(residuals) > 3 * std_resid, index=outlier_df.index, name='outlier')
    chat_df = pd.concat([chat_df, outliers], axis=1)
    chat_df['outlier'] = chat_df['outlier'].fillna(False).astype(bool)
    # added_df_outliers = chat_df[~chat_df.index.isin(added_df_no_outliers.index)]

    return chat_df


def import_and_clean_chat(file_path):
    """
    Import chat data from a file and clean it.
    Args:
        file_path (str): Path to the chat data file.
    Returns:
        DataFrame: Cleaned chat data with additional columns for errors and outliers.
    """
    # file_path = "WhatsApp Chat with 1 Million Beers 20250615 1357.zip"
    lines = load_whatsapp_chat_from_bucket('1-million-beers', file_path)

    # Parse chat lines and process the data
    chat_df = parse_chat_lines(lines)
    chat_df = process_chat_data(chat_df)

    # Filter for rows with a valid n_beers value
    chat_df = chat_df.dropna(subset=["n_beers"])

    # Errors where n_beers is too high or too low
    chat_df = beer_errors(chat_df)

    # Flag outliers based a linear trend
    chat_df = flag_outliers(chat_df)

    chat_df['error'] = np.select(
        [
            chat_df['outlier'],
            # chat_df['error_low_confirmed'], chat_df['error_high_confirmed'],
            chat_df['error_low'], chat_df['error_high'],
        ],
        [
            'outlier',
            # 'low_confirmed', 'high_confirmed',
            'low', 'high'
        ],
        default='none'
    )


    return chat_df