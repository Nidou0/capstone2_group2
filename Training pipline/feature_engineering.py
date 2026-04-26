import pandas as pd
import numpy as np
from config import TICKER_MAP


def feature_engineering(df: pd.DataFrame, window_size: int) -> pd.DataFrame:
    """
    This function takes in a DataFrame containing cleaned stock data
    and engineers new features. All features are in return/ratio space
    (no raw prices) to prevent the model from learning price-echoing shortcuts.

    Parameters:
    df (pd.DataFrame): A DataFrame containing cleaned stock data.
    window_size (int): The window size for calculating rolling statistics.
    Returns:
    pd.DataFrame: A DataFrame with engineered features.
    """
    df = df.copy()

    # --- Return-based lag features ---
    df['Log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Return_lag_2'] = df['Log_returns'].shift(1)
    df['Return_lag_5'] = df['Log_returns'].shift(4)

    # --- Rolling return features ---
    df[f'Rolling_log_returns_{window_size}d'] = df['Log_returns'].rolling(
        window=window_size, min_periods=1).sum()

    # --- Rolling volatility (coefficient of variation) and Bollinger position ---
    rolling_mean = df['Close'].rolling(window=window_size, min_periods=1).mean()
    rolling_std = df['Close'].rolling(window=window_size, min_periods=1).std()
    df[f'Rolling_cv_{window_size}d'] = rolling_std / rolling_mean.clip(lower=1e-10)
    df[f'Bollinger_pos_{window_size}d'] = (
        df['Close'] - rolling_mean) / rolling_std.clip(lower=1e-10)

    # --- RSI ---
    delta = df['Close'] - df['Close'].shift(1)
    gain = delta.clip(lower=0)
    loss = delta.clip(upper=0).abs()
    avg_gain = gain.rolling(window=window_size, min_periods=1).mean()
    avg_loss = loss.rolling(window=window_size, min_periods=1).mean()
    rs = avg_gain / avg_loss.clip(lower=1e-10)
    df[f'RSI_{window_size}d'] = 100 - (100 / (1 + rs))

    # --- MACD histogram (normalized by price) ---
    ema_12 = df['Close'].ewm(span=12, min_periods=1).mean()
    ema_26 = df['Close'].ewm(span=26, min_periods=1).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, min_periods=1).mean()
    df['MACD_hist'] = (macd_line - signal_line) / df['Close']

    # --- ATR (normalized by price) ---
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift(1)).abs()
    low_close = (df['Low'] - df['Close'].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df[f'ATR_{window_size}d'] = true_range.rolling(
        window=window_size, min_periods=1).mean() / df['Close']

    # --- Intraday features (normalized by price) ---
    df['Intraday_range'] = (df['High'] - df['Low']) / df['Close']
    df['Candle_body'] = (df['Close'] - df['Open']) / df['Close']
    df['Upper_shadow'] = (df['High'] - df[['Open', 'Close']].max(axis=1)) / df['Close']
    df['Lower_shadow'] = (df[['Open', 'Close']].min(axis=1) - df['Low']) / df['Close']

    # --- Volume log returns ---
    df['Volume_log_returns'] = np.log(df['Volume'].replace(
        0, 1e-10) / df['Volume'].shift(1).replace(0, 1e-10))

    # --- Target: log return (not raw price) ---
    df['Target_return'] = np.log(df['Close'].shift(-1) / df['Close'])

    return df


def merge_sentiment(ticker_df: pd.DataFrame, sentiment_df: pd.DataFrame) -> pd.DataFrame:
    """
    Left-joins pre-computed daily sentiment features onto the price DataFrame.
    The join is on the normalized date index. Rows with no matching sentiment
    (dates outside the sentiment coverage window) are filled with 0.0 so
    downstream dropna() does not silently discard them.

    Parameters:
        ticker_df (pd.DataFrame): Feature-engineered price DataFrame for one ticker.
        sentiment_df (pd.DataFrame): Sentiment DataFrame indexed by date for that ticker.
    Returns:
        pd.DataFrame: ticker_df with sentiment columns appended.
    """
    # Normalize both indices to date only (strip time component)
    ticker_df.index = ticker_df.index.normalize()
    sentiment_df.index = sentiment_df.index.normalize()

    merged = ticker_df.join(sentiment_df, how='left')

    # Any price rows outside sentiment coverage -> fill with 0
    sentiment_cols = [c for c in sentiment_df.columns if c != 'article_count']
    merged[sentiment_cols] = merged[sentiment_cols].fillna(0.0)

    # article_count outside coverage -> 0
    if 'article_count' in merged.columns:
        merged['article_count'] = merged['article_count'].fillna(0).astype(int)

    return merged


def apply_feature_engineering(
    data: pd.DataFrame,
    ticker_map: dict[str, str],
    window_size: int,
    sentiment_data: dict = None   # pass None for price-only run (config A)
) -> pd.DataFrame:
    """
    Applies feature engineering to all tickers. If sentiment_data is provided,
    sentiment features are merged in (config B). Otherwise runs price-only (config A).

    Parameters:
    data (pd.DataFrame): A DataFrame containing cleaned stock data.
    ticker_map (dict): A dictionary mapping stock tickers to company names.
    window_size (int): The window size for calculating rolling statistics.
    sentiment_data (dict | None): Optional dict of {ticker: sentiment_df}.
    Returns:
    pd.DataFrame: A DataFrame with engineered features for all stocks.
    """
    results = []
    for ticker in ticker_map:
        ticker_df = data[data['Ticker'] == ticker].copy()
        engineered_df = feature_engineering(ticker_df, window_size)

        # Merge sentiment if provided
        if sentiment_data and ticker in sentiment_data:
            engineered_df = merge_sentiment(engineered_df, sentiment_data[ticker])

        engineered_df = engineered_df.dropna()
        results.append(engineered_df)
        mode = "price+sentiment" if (sentiment_data and ticker in sentiment_data) else "price-only"
        print(
            f"✅ {ticker_map[ticker]} ({ticker}): {mode}, {window_size}d window — {len(engineered_df)} rows")

    return pd.concat(results)


def initializer(
    windows: list[int],
    cleaned_df: pd.DataFrame,
    TICKER_MAP: dict[str, str],
    sentiment_data: dict = None   # pass None for price-only run
) -> dict[int, pd.DataFrame]:
    """
    Initializes feature engineering for all window sizes.

    Parameters:
    windows (list[int]): Window sizes to compute features for.
    cleaned_df (pd.DataFrame): Cleaned stock data.
    TICKER_MAP (dict): Ticker to company name mapping.
    sentiment_data (dict | None): Optional sentiment data per ticker.
    Returns:
    dict: {window_size: featured_DataFrame}
    """
    featured_data = {}
    for window in windows:
        featured_data[window] = apply_feature_engineering(
            cleaned_df, TICKER_MAP, window, sentiment_data=sentiment_data)

    for window, df in featured_data.items():
        print(f"Window {window}d: {df.shape[0]} rows, {df.shape[1]} columns")

    return featured_data
