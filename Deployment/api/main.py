from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np
import pandas as pd
import onnxruntime as ort
import os

app = FastAPI()

TICKER_MAP = {
    "1155.KL": "Maybank",
    "1295.KL": "Public Bank",
    "1023.KL": "CIMB Group",
    "5347.KL": "Tenaga Nasional",
    "5225.KL": "IHH Healthcare",
    "8869.KL": "Press Metal",
    "5819.KL": "Hong Leong Bank",
    "5285.KL": "SD Guthrie",
    "6947.KL": "CelcomDigi",
    "5211.KL": "Sunway"
}

MODEL_CONFIG = {
    "1155.KL": {"type": "lgbm", "window": 60},
    "1295.KL": {"type": "lgbm", "window": 20},
    "1023.KL": {"type": "lgbm", "window": 20},
    "5347.KL": {"type": "xgb",  "window": 5},
    "5225.KL": {"type": "lgbm", "window": 20},
    "8869.KL": {"type": "xgb",  "window": 10},
    "5819.KL": {"type": "xgb",  "window": 5},
    "5285.KL": {"type": "xgb",  "window": 20},
    "6947.KL": {"type": "lgbm", "window": 10},
    "5211.KL": {"type": "lgbm", "window": 60},
}

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models_saved")
_session_cache: dict = {}


class StockPredictionOutput(BaseModel):
    ticker: str
    name: str
    current_price: float
    end_close_price: float
    pct_change: float
    direction: str
    rsi: float
    macd_hist: float
    bollinger_pos: float


def load_session(ticker: str) -> ort.InferenceSession:
    if ticker in _session_cache:
        return _session_cache[ticker]
    config = MODEL_CONFIG[ticker]
    path = os.path.join(MODELS_DIR, f"{config['type']}_{ticker}_{config['window']}d.onnx")
    session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    _session_cache[ticker] = session
    return session


def compute_features(df: pd.DataFrame, window: int) -> np.ndarray:
    df = df.copy()
    df["Log_returns"] = np.log(df["Close"] / df["Close"].shift(1))
    df["Return_lag_2"] = df["Log_returns"].shift(1)
    df["Return_lag_5"] = df["Log_returns"].shift(4)
    df[f"Rolling_log_returns_{window}d"] = df["Log_returns"].rolling(window=window, min_periods=1).sum()
    rolling_mean = df["Close"].rolling(window=window, min_periods=1).mean()
    rolling_std = df["Close"].rolling(window=window, min_periods=1).std().fillna(0).replace(0, 1e-10)
    df[f"Rolling_cv_{window}d"] = rolling_std / rolling_mean
    df[f"Bollinger_pos_{window}d"] = (df["Close"] - rolling_mean) / rolling_std
    delta = df["Close"] - df["Close"].shift(1)
    avg_gain = delta.clip(lower=0).rolling(window=window, min_periods=1).mean()
    avg_loss = delta.clip(upper=0).abs().rolling(window=window, min_periods=1).mean()
    df[f"RSI_{window}d"] = 100 - (100 / (1 + avg_gain / avg_loss.clip(lower=1e-10)))
    ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD_hist"] = (ema_12 - ema_26) / df["Close"]
    prev_close = df["Close"].shift(1)
    true_range = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - prev_close).abs(),
        (df["Low"] - prev_close).abs()
    ], axis=1).max(axis=1)
    df[f"ATR_{window}d"] = true_range.rolling(window=window, min_periods=1).mean() / df["Close"]
    df["Intraday_range"] = (df["High"] - df["Low"]) / df["Close"]
    df["Candle_body"] = (df["Close"] - df["Open"]) / df["Close"]
    df["Upper_shadow"] = (df["High"] - df[["Open", "Close"]].max(axis=1)) / df["Close"]
    df["Lower_shadow"] = (df[["Open", "Close"]].min(axis=1) - df["Low"]) / df["Close"]
    df["Volume_log_returns"] = np.log(
        df["Volume"].replace(0, 1e-10) / df["Volume"].shift(1).replace(0, 1e-10)
    )
    cols_to_drop = [c for c in ["Dividends", "Stock Splits"] if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    return df.iloc[-1].values.astype(np.float32).reshape(1, -1)


def get_latest_indicators(df: pd.DataFrame, window: int) -> dict:
    """Compute the last RSI, MACD histogram, and Bollinger position for display."""
    df = df.copy()

    delta = df["Close"] - df["Close"].shift(1)
    avg_gain = delta.clip(lower=0).rolling(window=window, min_periods=1).mean()
    avg_loss = delta.clip(upper=0).abs().rolling(window=window, min_periods=1).mean()
    rsi = 100 - (100 / (1 + avg_gain / avg_loss.clip(lower=1e-10)))

    ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd_hist = (ema_12 - ema_26) / df["Close"]

    rolling_mean = df["Close"].rolling(window=window, min_periods=1).mean()
    rolling_std = df["Close"].rolling(window=window, min_periods=1).std().fillna(0).replace(0, 1e-10)
    bollinger_pos = (df["Close"] - rolling_mean) / rolling_std

    return {
        "rsi": round(float(rsi.iloc[-1]), 1),
        "macd_hist": round(float(macd_hist.iloc[-1]), 6),
        "bollinger_pos": round(float(bollinger_pos.iloc[-1]), 2),
    }


@app.get("/api/stocks", response_model=list[StockPredictionOutput])
async def get_top_stocks():
    result = []
    for symbol in TICKER_MAP:
        try:
            ticker_obj = yf.Ticker(symbol)
            current_price = float(ticker_obj.fast_info["last_price"])
            df = ticker_obj.history(period="1y")

            config = MODEL_CONFIG[symbol]
            window = config["window"]

            if df.empty or len(df) < window + 10:
                raise ValueError(f"Insufficient data for {symbol}")

            session = load_session(symbol)
            X = compute_features(df, window)
            input_name = session.get_inputs()[0].name
            output_name = session.get_outputs()[0].name
            log_return = float(session.run([output_name], {input_name: X})[0].flatten()[0])

            end_close_price = round(current_price * np.exp(log_return), 2)
            pct_change = round(((end_close_price - current_price) / current_price) * 100, 2)

            if pct_change > 0.5:
                direction = "BUY"
            elif pct_change < -0.5:
                direction = "SELL"
            else:
                direction = "HOLD"

            indicators = get_latest_indicators(df, window)

            result.append({
                "ticker": symbol.replace(".KL", ""),
                "name": TICKER_MAP[symbol],
                "current_price": round(current_price, 2),
                "end_close_price": end_close_price,
                "pct_change": pct_change,
                "direction": direction,
                **indicators,
            })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            result.append({
                "ticker": symbol.replace(".KL", ""),
                "name": TICKER_MAP.get(symbol, "Unknown"),
                "current_price": 0.0,
                "end_close_price": 0.0,
                "pct_change": 0.0,
                "direction": "ERROR",
                "rsi": 0.0,
                "macd_hist": 0.0,
                "bollinger_pos": 0.0,
            })

    return result


@app.get("/api/analytics")
async def get_analytics():
    tickers = list(TICKER_MAP.keys())
    try:
        raw = yf.download(
            tickers, period="3y", interval="1d",
            auto_adjust=True, progress=False
        )

        close_df = raw["Close"]
        volume_df = raw["Volume"]

        try:
            monthly_close = close_df.resample("ME").last()
        except Exception:
            monthly_close = close_df.resample("M").last()

        recent_close = close_df.tail(60)
        recent_volume = volume_df.tail(60)

        daily_returns = close_df.pct_change().dropna()
        corr_matrix = daily_returns.corr()

        monthly_dates = [d.strftime("%Y-%m") for d in monthly_close.index]
        recent_dates = [d.strftime("%b %d") for d in recent_close.index]

        result = {
            "monthly_dates": monthly_dates,
            "recent_dates": recent_dates,
            "tickers": tickers,
            "ticker_names": TICKER_MAP,
            "monthly_closes": {},
            "recent_volumes": {},
            "stats": {},
            "correlation": []
        }

        for ticker in tickers:
            closes = close_df[ticker].dropna()
            monthly = monthly_close[ticker].ffill()
            volumes = recent_volume[ticker].fillna(0)

            current = float(closes.iloc[-1])
            first = float(closes.iloc[0])
            return_pct = round((current - first) / first * 100, 1)
            mean_vol_m = round(float(volume_df[ticker].mean() / 1e6), 1)

            result["monthly_closes"][ticker] = [
                round(float(v), 3) if pd.notna(v) else None for v in monthly
            ]
            result["recent_volumes"][ticker] = [
                round(float(v) / 1e6, 2) if pd.notna(v) and float(v) > 0 else 0
                for v in volumes
            ]
            result["stats"][ticker] = {
                "current": round(current, 2),
                "min": round(float(closes.min()), 2),
                "max": round(float(closes.max()), 2),
                "mean": round(float(closes.mean()), 2),
                "std": round(float(closes.std()), 2),
                "mean_vol": mean_vol_m,
                "return_pct": return_pct,
                "data_points": int(len(closes)),
            }

        corr_values = []
        for t1 in tickers:
            row = []
            for t2 in tickers:
                try:
                    v = float(corr_matrix.loc[t1, t2])
                    row.append(round(v, 2) if not np.isnan(v) else 0.0)
                except Exception:
                    row.append(0.0)
            corr_values.append(row)
        result["correlation"] = corr_values

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
