import tensorflow as tf
from data_ingestion import ingestor
from feature_engineering import initializer
from sentiment_ingestion import load_all_sentiment, cutoff_sentiment_to_price_range
from preprocessing import pre_processing_ml, create_sequences, scale_data, create_train_test_val_split
from models.xgboost import build_xgb
from models.randomforest import build_rf
from models.lightbgm import build_lbm
from models.cnn import build_cnn
from models.lstm import build_lstm
from models.transformer import build_transformer
from training import boost_train_model, rf_train_model, train_model
from evaluation import evaluate_model
from config import (TICKER_MAP, WINDOWS, RUN_INGESTION, RUN_FEATURE_ENGINEERING,
                    RUN_TRAINING, MODELS_TO_RUN, WINDOWS_TO_RUN, CLEANED_DATA_PATH,
                    FEATURED_DATA_PATH, FEATURED_SENTIMENT_DATA_PATH, USE_SENTIMENT,
                    FILTERS, UNITS, NUM_HEADS, KEY_DIM, FF_DIM)
import lightgbm as lgb
import xgboost as xgb
import pandas as pd
import numpy as np
import joblib
import os

DL_MODELS = {'cnn', 'lstm', 'transformer'}

if __name__ == "__main__":
    np.random.seed(42)
    tf.random.set_seed(42)
    os.makedirs('data', exist_ok=True)

    if RUN_INGESTION:
        cleaned_df = ingestor(TICKER_MAP)
        cleaned_df.to_parquet(CLEANED_DATA_PATH)
    else:
        cleaned_df = pd.read_parquet(CLEANED_DATA_PATH)

    if RUN_FEATURE_ENGINEERING:
        sentiment_data = None
        if USE_SENTIMENT:
            sentiment_data = load_all_sentiment(TICKER_MAP)
            sentiment_data = cutoff_sentiment_to_price_range(
                cleaned_df, sentiment_data, TICKER_MAP
            )

        featured_data = initializer(
            WINDOWS, cleaned_df, TICKER_MAP, sentiment_data=sentiment_data
        )
        featured_data_path = (
            FEATURED_SENTIMENT_DATA_PATH if USE_SENTIMENT else FEATURED_DATA_PATH
        )
        for window in WINDOWS:
            featured_data[window].to_parquet(
                featured_data_path.format(window=window))
    else:
        featured_data = {}
        featured_data_path = (
            FEATURED_SENTIMENT_DATA_PATH if USE_SENTIMENT else FEATURED_DATA_PATH
        )
        for window in WINDOWS:
            featured_data[window] = pd.read_parquet(
                featured_data_path.format(window=window))

    results = {}
    os.makedirs('models_saved', exist_ok=True)
    os.makedirs('evaluation_results', exist_ok=True)

    if RUN_TRAINING:
        for ticker in TICKER_MAP:
            results[ticker] = {}
            for window in WINDOWS_TO_RUN:
                results[ticker][window] = {}

                # --- ML models ---
                X, y, close_prices = pre_processing_ml(featured_data[window], ticker)
                X_train, y_train, X_val, y_val, X_test, y_test = create_train_test_val_split(
                    X, y)

                val_end = int(len(X) * 0.90)
                close_test = close_prices[val_end:]

                if 'xgb' in MODELS_TO_RUN:
                    xgb_model = build_xgb()
                    xgb_model, _ = boost_train_model(
                        xgb_model, X_train, y_train, X_val, y_val)
                    results[ticker][window]['xgb'] = evaluate_model(
                        xgb_model, X_test, y_test, close_prices=close_test)
                    xgb_model.save_model(
                        f'models_saved/xgb_{ticker}_{window}d.json')

                if 'rf' in MODELS_TO_RUN:
                    rf_model = build_rf()
                    rf_model, _ = rf_train_model(
                        rf_model, X_train, y_train, X_val, y_val)
                    results[ticker][window]['rf'] = evaluate_model(
                        rf_model, X_test, y_test, close_prices=close_test)
                    joblib.dump(rf_model,
                                f'models_saved/rf_{ticker}_{window}d.pkl')

                if 'lgbm' in MODELS_TO_RUN:
                    lgbm_model = build_lbm()
                    lgbm_model, _ = boost_train_model(
                        lgbm_model, X_train, y_train, X_val, y_val)
                    results[ticker][window]['lgbm'] = evaluate_model(
                        lgbm_model, X_test, y_test, close_prices=close_test)
                    lgbm_model.booster_.save_model(
                        f'models_saved/lgbm_{ticker}_{window}d.txt')

                # --- DL models ---
                if any(m in MODELS_TO_RUN for m in DL_MODELS):
                    X_dl, y_dl, close_prices_dl = create_sequences(
                        featured_data[window], timesteps=window, ticker=ticker)
                    X_train_dl, y_train_dl, X_val_dl, y_val_dl, X_test_dl, y_test_dl = create_train_test_val_split(
                        X_dl, y_dl)

                    val_end_dl = int(len(X_dl) * 0.90)
                    close_test_dl = close_prices_dl[val_end_dl:]

                    X_train_dl, X_val_dl, X_test_dl, y_train_dl, y_val_dl, y_test_dl, _, y_scaler_dl = scale_data(
                        X_train_dl, X_val_dl, X_test_dl, y_train_dl, y_val_dl, y_test_dl)

                    input_shape = (window, X_train_dl.shape[2])

                    if 'cnn' in MODELS_TO_RUN:
                        cnn_model = build_cnn(input_shape=input_shape, filters=FILTERS)
                        cnn_model, _ = train_model(
                            cnn_model, X_train_dl, y_train_dl, X_val_dl, y_val_dl)
                        results[ticker][window]['cnn'] = evaluate_model(
                            cnn_model, X_test_dl, y_test_dl,
                            y_scaler=y_scaler_dl, close_prices=close_test_dl)
                        cnn_model.save(f'models_saved/cnn_{ticker}_{window}d.keras')

                    if 'lstm' in MODELS_TO_RUN:
                        lstm_model = build_lstm(input_shape=input_shape, units=UNITS)
                        lstm_model, _ = train_model(
                            lstm_model, X_train_dl, y_train_dl, X_val_dl, y_val_dl)
                        results[ticker][window]['lstm'] = evaluate_model(
                            lstm_model, X_test_dl, y_test_dl,
                            y_scaler=y_scaler_dl, close_prices=close_test_dl)
                        lstm_model.save(f'models_saved/lstm_{ticker}_{window}d.keras')

                    if 'transformer' in MODELS_TO_RUN:
                        transformer_model = build_transformer(
                            input_shape=input_shape, num_heads=NUM_HEADS,
                            key_dim=KEY_DIM, ff_dim=FF_DIM)
                        transformer_model, _ = train_model(
                            transformer_model, X_train_dl, y_train_dl, X_val_dl, y_val_dl)
                        results[ticker][window]['transformer'] = evaluate_model(
                            transformer_model, X_test_dl, y_test_dl,
                            y_scaler=y_scaler_dl, close_prices=close_test_dl)
                        transformer_model.save(
                            f'models_saved/transformer_{ticker}_{window}d.keras')

                print(f"\n-- {TICKER_MAP[ticker]} | Window {window}d Results")
                for model_name, metrics in results[ticker][window].items():
                    print(
                        f"{model_name} MAE={metrics['MAE']:.4f} | RMSE={metrics['RMSE']:.4f} | "
                        f"R2={metrics['R2']:.4f} | MAPE={metrics['MAPE']:.4f} | DA={metrics['DA']:.4f}")

    else:
        for ticker in TICKER_MAP:
            results[ticker] = {}
            for window in WINDOWS_TO_RUN:
                results[ticker][window] = {}

                # --- ML models ---
                X, y, close_prices = pre_processing_ml(featured_data[window], ticker)
                X_train, y_train, X_val, y_val, X_test, y_test = create_train_test_val_split(
                    X, y)

                val_end = int(len(X) * 0.90)
                close_test = close_prices[val_end:]

                if 'xgb' in MODELS_TO_RUN:
                    xgb_model = xgb.XGBRegressor()
                    xgb_model.load_model(f'models_saved/xgb_{ticker}_{window}d.json')
                    results[ticker][window]['xgb'] = evaluate_model(
                        xgb_model, X_test, y_test, close_prices=close_test)

                if 'rf' in MODELS_TO_RUN:
                    rf_model = joblib.load(f'models_saved/rf_{ticker}_{window}d.pkl')
                    results[ticker][window]['rf'] = evaluate_model(
                        rf_model, X_test, y_test, close_prices=close_test)

                if 'lgbm' in MODELS_TO_RUN:
                    lgbm_model = lgb.Booster(
                        model_file=f'models_saved/lgbm_{ticker}_{window}d.txt')
                    results[ticker][window]['lgbm'] = evaluate_model(
                        lgbm_model, X_test, y_test, close_prices=close_test)

                # --- DL models ---
                if any(m in MODELS_TO_RUN for m in DL_MODELS):
                    X_dl, y_dl, close_prices_dl = create_sequences(
                        featured_data[window], timesteps=window, ticker=ticker)
                    X_train_dl, y_train_dl, X_val_dl, y_val_dl, X_test_dl, y_test_dl = create_train_test_val_split(
                        X_dl, y_dl)

                    val_end_dl = int(len(X_dl) * 0.90)
                    close_test_dl = close_prices_dl[val_end_dl:]

                    X_train_dl, X_val_dl, X_test_dl, y_train_dl, y_val_dl, y_test_dl, _, y_scaler_dl = scale_data(
                        X_train_dl, X_val_dl, X_test_dl, y_train_dl, y_val_dl, y_test_dl)

                    if 'cnn' in MODELS_TO_RUN:
                        cnn_model = tf.keras.models.load_model(
                            f'models_saved/cnn_{ticker}_{window}d.keras')
                        results[ticker][window]['cnn'] = evaluate_model(
                            cnn_model, X_test_dl, y_test_dl,
                            y_scaler=y_scaler_dl, close_prices=close_test_dl)

                    if 'lstm' in MODELS_TO_RUN:
                        lstm_model = tf.keras.models.load_model(
                            f'models_saved/lstm_{ticker}_{window}d.keras')
                        results[ticker][window]['lstm'] = evaluate_model(
                            lstm_model, X_test_dl, y_test_dl,
                            y_scaler=y_scaler_dl, close_prices=close_test_dl)

                    if 'transformer' in MODELS_TO_RUN:
                        transformer_model = tf.keras.models.load_model(
                            f'models_saved/transformer_{ticker}_{window}d.keras')
                        results[ticker][window]['transformer'] = evaluate_model(
                            transformer_model, X_test_dl, y_test_dl,
                            y_scaler=y_scaler_dl, close_prices=close_test_dl)

                print(f"\n-- {TICKER_MAP[ticker]} | Window {window}d Results")
                for model_name, metrics in results[ticker][window].items():
                    print(
                        f"{model_name} MAE={metrics['MAE']:.4f} | RMSE={metrics['RMSE']:.4f} | "
                        f"R2={metrics['R2']:.4f} | MAPE={metrics['MAPE']:.4f} | DA={metrics['DA']:.4f}")

    rows = []
    for ticker, windows in results.items():
        for window, models in windows.items():
            for model_name, metrics in models.items():
                rows.append({
                    'ticker': ticker,
                    'company': TICKER_MAP[ticker],
                    'window': window,
                    'model': model_name,
                    'MAE': metrics['MAE'],
                    'RMSE': metrics['RMSE'],
                    'R2': metrics['R2'],
                    'MAPE': metrics['MAPE'],
                    'DA': metrics['DA'],
                    'Naive_MAE': metrics['Naive_MAE'],
                    'Naive_RMSE': metrics['Naive_RMSE']
                })
    results_df = pd.DataFrame(rows)
    results_df.to_csv('evaluation_results/training_metrics.csv', index=False)
