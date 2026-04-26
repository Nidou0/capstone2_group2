import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error


def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray,
                   y_scaler: StandardScaler = None, close_prices: np.ndarray = None) -> dict:
    predictions = model.predict(X_test)
    y_pred = predictions.flatten()

    # Inverse scale to get raw log returns
    if y_scaler is not None:
        y_pred = y_scaler.inverse_transform(y_pred.reshape(-1, 1)).flatten()
        y_test = y_scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    # Convert log returns to prices for MAPE calculation
    if close_prices is not None:
        y_pred_price = close_prices * np.exp(y_pred)
        y_actual_price = close_prices * np.exp(y_test)
        mape = mean_absolute_percentage_error(y_actual_price, y_pred_price)
        naive_price = close_prices  # naive = predict no change
        naive_mae = mean_absolute_error(y_actual_price, naive_price)
        naive_rmse = np.sqrt(mean_squared_error(y_actual_price, naive_price))
    else:
        mape = 0.0
        naive_mae = 0.0
        naive_rmse = 0.0

    # Metrics on returns
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # Directional accuracy: sign of predicted return vs sign of actual return
    da = np.mean(np.sign(y_pred) == np.sign(y_test))

    print(f"MAE: {mae:.6f} | RMSE: {rmse:.6f} | R²: {r2:.4f} | MAPE: {mape:.4f} | DA: {da:.4f}")
    print(f"Naive Baseline — MAE: {naive_mae:.4f} | RMSE: {naive_rmse:.4f}")

    return {'MAE': mae, 'RMSE': rmse, 'R2': r2, 'MAPE': mape, 'DA': da,
            'Naive_MAE': naive_mae, 'Naive_RMSE': naive_rmse}
