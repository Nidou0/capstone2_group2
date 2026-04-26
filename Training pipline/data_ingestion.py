import yfinance as yf
import pandas as pd
import numpy as np
from config import TICKER_MAP, PRICE_COLS


def fetch_stock_data(ticker, company_name):
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="5y")
        if not history.empty:
            if history.index.tz is not None:
                history.index = history.index.tz_localize(None)
            history["Ticker"] = ticker
            history["Company"] = company_name
            return history  # ✅ return full history
        else:
            print(f"No data found for {ticker}")
            return None
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def ingestor(TICKER_MAP: dict[str, str]) -> pd.DataFrame:
    all_frames = []
    for ticker, name in TICKER_MAP.items():
        stock_data = fetch_stock_data(ticker, name)
        if stock_data is not None:
            print(f"✅ {name} ({ticker}): {len(stock_data)} rows fetched")
            all_frames.append(stock_data)  # ✅ collect all results
    # Combine into one DataFrame
    data = pd.concat(all_frames) if all_frames else pd.DataFrame()
    cleaned_data = clean_all_stocks(data, TICKER_MAP)
    return cleaned_data


def remove_non_trading_days(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df.index.weekday < 5]
    df = df.dropna(subset=PRICE_COLS, how='all')
    df = df[df['Volume'] > 0]
    return df


def impute_missing_values(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    df = df.copy()

    for col in PRICE_COLS:
        mask = df[col].isna()
        if mask.any():
            rolling_mean = df[col].rolling(
                window=window, min_periods=1).mean()  # ✅ uses parameter
            df.loc[mask, col] = rolling_mean[mask]

    # ✅ outside loop
    vol_mask = df['Volume'].isna()
    if vol_mask.any():
        rolling_median = df['Volume'].rolling(
            window=window, min_periods=1).median()
        # ✅ only fills NaNs
        df.loc[vol_mask, 'Volume'] = rolling_median[vol_mask]

    # ✅ outside loop
    return df.ffill()


def validate_columns(df: pd.DataFrame, ticker: str) -> bool:
    required = set(PRICE_COLS + ["Volume"])
    missing = required - set(df.columns)
    if missing:
        print(f"⚠️ {ticker}: Missing columns: {missing}")
        return False
    # ✅ explicit True
    return True


def clean_stock_data(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    df = remove_non_trading_days(df)
    df = impute_missing_values(df, window=window)
    return df


def clean_all_stocks(
    data: pd.DataFrame,
    ticker_map: dict[str, str],
    window: int = 5
) -> pd.DataFrame:
    cleaned_df = []

    for ticker, company in ticker_map.items():
        if ticker not in data['Ticker'].unique():
            print(f"⚠️  {ticker} ({company}) not found in data — skipping.")
            continue

        ticker_df = data[data['Ticker'] == ticker].copy()

        if not validate_columns(ticker_df, ticker):
            continue

        cleaned = clean_stock_data(ticker_df, window=window)
        removed = len(ticker_df) - len(cleaned)
        print(
            f"✅ {company} ({ticker}): {len(ticker_df)} → {len(cleaned)} rows ({removed} removed)")
        cleaned_df.append(cleaned)

    return pd.concat(cleaned_df) if cleaned_df else pd.DataFrame()
