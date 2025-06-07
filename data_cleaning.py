import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def beer_errors(chat_df):
    """
    Flag rows with errors in beer counts.
    """

    # # Remove rows where n_beers greater than row after it
    # chat_df = chat_df[chat_df['n_beers'] <= chat_df['n_beers'].shift(-1)]
    # chat_df = chat_df[chat_df['n_beers'] <= chat_df['n_beers'].shift(-2)]
    chat_df.loc[:,'error_high'] = (chat_df['n_beers'] > chat_df['n_beers'].shift(-1)) | (chat_df['n_beers'] > chat_df['n_beers'].shift(-2))


    # # Remove rows where n_beers is less than the previous row's n_beers
    # chat_df = chat_df[chat_df['n_beers'] >= chat_df['n_beers'].shift(1)]
    # chat_df = chat_df[chat_df['n_beers'] >= chat_df['n_beers'].shift(2)]
    chat_df.loc[:,'error_low'] = (chat_df['n_beers'] < chat_df['n_beers'].shift(1)) | (chat_df['n_beers'] < chat_df['n_beers'].shift(2)) & (chat_df['error_high'] == False)

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
    chat_df['outlier'] = chat_df['outlier'].fillna(False)
    # added_df_outliers = chat_df[~chat_df.index.isin(added_df_no_outliers.index)]

    return chat_df