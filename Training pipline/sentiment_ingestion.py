import pandas as pd
import numpy as np
import os
from config import SENTIMENT_DIR, SENTIMENT_FILL_STRATEGY

# Sentiment columns produced by FinBERT pipeline
SENTIMENT_COLS = [
    'sentiment_score_title',
    'prob_pos_title',
    'prob_neu_title',
    'prob_neg_title',
    'dir_positive_title',
    'dir_neutral_title',
    'dir_negative_title',
    'confidence_title',
    'strength_title',
]


def load_sentiment(ticker: str) -> pd.DataFrame:
    """
    Loads the pre-computed daily sentiment CSV for a single ticker.
    Parses trading_day with dayfirst=True (d/m/yyyy format).
    Adds has_news flag, then fills zero-sentiment no-news days
    according to SENTIMENT_FILL_STRATEGY in config.

    Parameters:
        ticker (str): Ticker string e.g. '1023.KL'
    Returns:
        pd.DataFrame: Indexed by normalized date, sentiment features + has_news.
    """
    # Build filename: '1023.KL' -> '1023_KL_title.csv'
    fname = ticker.replace('.', '_') + '_title.csv'
    fpath = os.path.join(SENTIMENT_DIR, fname)

    if not os.path.exists(fpath):
        print(f"⚠️  Sentiment file not found for {ticker}: {fpath}")
        return pd.DataFrame()

    df = pd.read_csv(fpath)
    df['trading_day'] = pd.to_datetime(df['trading_day'], dayfirst=True)
    df = df.set_index('trading_day')
    df.index = df.index.normalize()  # strip any time component

    # Binary flag: model can learn "no news" vs actual neutral
    df['has_news'] = (df['article_count'] > 0).astype(int)

    # Replace zero-filled no-news rows with NaN before imputation
    no_news_mask = df['article_count'] == 0
    df.loc[no_news_mask, SENTIMENT_COLS] = np.nan

    # Fill strategy
    if SENTIMENT_FILL_STRATEGY == 'ffill':
        # Carry forward last known sentiment
        df[SENTIMENT_COLS] = df[SENTIMENT_COLS].ffill()
        # Any leading NaNs (no prior news) fall back to neutral
        df[SENTIMENT_COLS] = df[SENTIMENT_COLS].fillna(0.0)
    elif SENTIMENT_FILL_STRATEGY == 'neutral':
        # Flat neutral baseline: score=0, probs=1/3, dirs=0, conf=0, strength=1/3
        neutral_vals = {
            'sentiment_score_title': 0.0,
            'prob_pos_title': 1/3,
            'prob_neu_title': 1/3,
            'prob_neg_title': 1/3,
            'dir_positive_title': 0.0,
            'dir_neutral_title': 1.0,
            'dir_negative_title': 0.0,
            'confidence_title': 0.0,
            'strength_title': 1/3,
        }
        for col, val in neutral_vals.items():
            df[col] = df[col].fillna(val)
    else:
        raise ValueError(
            f"Unknown SENTIMENT_FILL_STRATEGY: '{SENTIMENT_FILL_STRATEGY}'. "
            "Use 'ffill' or 'neutral'."
        )

    # Keep only what we need
    keep_cols = SENTIMENT_COLS + ['has_news', 'article_count']
    return df[[c for c in keep_cols if c in df.columns]]


def load_all_sentiment(ticker_map: dict[str, str]) -> dict[str, pd.DataFrame]:
    """
    Loads sentiment data for all tickers in ticker_map.

    Parameters:
        ticker_map (dict): Maps ticker -> company name.
    Returns:
        dict: Maps ticker -> sentiment DataFrame indexed by date.
    """
    sentiment_data = {}
    for ticker, company in ticker_map.items():
        df = load_sentiment(ticker)
        if not df.empty:
            sentiment_data[ticker] = df
            print(f"✅ {company} ({ticker}): sentiment loaded — "
                  f"{(df['has_news'] == 1).sum()} news days, "
                  f"{(df['has_news'] == 0).sum()} no-news days")
        else:
            print(f"⚠️  {company} ({ticker}): no sentiment data — skipping sentiment merge")
    return sentiment_data


def cutoff_sentiment_to_price_range(
    cleaned_df: pd.DataFrame,
    sentiment_data: dict[str, pd.DataFrame],
    ticker_map: dict[str, str]
) -> dict[str, pd.DataFrame]:
    """
    Trims each ticker's sentiment time series to the inclusive date range
    available in price data for that same ticker.
    """
    cutoff_data: dict[str, pd.DataFrame] = {}

    for ticker, company in ticker_map.items():
        if ticker not in sentiment_data:
            continue

        price_ticker_df = cleaned_df[cleaned_df['Ticker'] == ticker]
        if price_ticker_df.empty:
            print(f"⚠️  {company} ({ticker}): no price data — skipping sentiment cutoff")
            continue

        price_dates = pd.to_datetime(price_ticker_df.index).tz_localize(None).normalize()
        price_start = price_dates.min()
        price_end = price_dates.max()

        sentiment_df = sentiment_data[ticker].copy()
        sentiment_df.index = pd.to_datetime(sentiment_df.index).normalize()
        trimmed = sentiment_df[
            (sentiment_df.index >= price_start) & (sentiment_df.index <= price_end)
        ].copy()

        print(
            f"✅ {company} ({ticker}): sentiment cutoff {price_start.date()} to {price_end.date()} "
            f"({len(sentiment_df)} -> {len(trimmed)} rows)"
        )
        cutoff_data[ticker] = trimmed

    return cutoff_data
