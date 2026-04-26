import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def pre_processing_ml(data: pd.DataFrame, ticker: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ticker_df = data[data['Ticker'] == ticker]
    close_prices = ticker_df['Close'].values
    y = ticker_df['Target_return'].values
    X = ticker_df.drop(columns=['Dividends', 'Stock Splits',
                       'Ticker', 'Company', 'Target_return']).values
    return X, y, close_prices


def create_sequences(data: pd.DataFrame, timesteps: int, ticker: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    This function takes in the cleaned data and timesteps.
    It applies transformations to the data to create sequences so the data can be used for
    Deep Learning. Also returns the close prices for each sequence's last timestep,
    needed to convert return predictions back to prices at evaluation time.
    Parameters:
    data (pd.DataFrame): A DataFrame containing cleaned stock data.
    timesteps (int): The timesteps to look back on.
    ticker (str): The stock ticker to filter for.
    Returns:
    tuple: X sequences, y targets (log returns), and close prices for the last timestep.
    """
    X_list = []
    y_list = []
    close_list = []

    ticker_df = data[data['Ticker'] == ticker]
    X_data = ticker_df.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume',
                                     'Dividends', 'Stock Splits', 'Ticker', 'Company',
                                     'Target_return']).values
    y_data = ticker_df['Target_return'].values
    close_data = ticker_df['Close'].values
    for i in range(0, len(X_data) - timesteps + 1):
        X_list.append(X_data[i: i + timesteps])
        y_list.append(y_data[i + timesteps - 1])
        close_list.append(close_data[i + timesteps - 1])
    X = np.array(X_list)
    y = np.array(y_list)
    close_prices = np.array(close_list)
    return X, y, close_prices


def create_train_test_val_split(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    This function takes in two numpy arrays X and y, and return a tuple of 6 arrays.
    It splits the data to train, validation, test splits following 70-20-10.
    Parameters:
    X (np.ndarray): A numpy array containing the features.
    y (np.ndarray): A numpy array containing the target variable.
    Returns:
    tuple: A tuple containing the train, validation and test splits for both X and y.
    """
    train_end = int(len(X) * 0.70)
    val_end = int(len(X) * 0.90)

    X_train = X[:train_end]
    X_val = X[train_end:val_end]
    X_test = X[val_end:]
    y_train = y[:train_end]
    y_val = y[train_end:val_end]
    y_test = y[val_end:]
    print(f'Train:{X_train.shape} | Val:{X_val.shape} | Test:{X_test.shape}')
    return X_train, y_train, X_val, y_val, X_test, y_test


def scale_data(X_train: np.ndarray, X_val: np.ndarray, X_test: np.ndarray,
               y_train: np.ndarray, y_val: np.ndarray, y_test: np.ndarray
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, StandardScaler]:
    """
    This function takes in X and y arrays for train, val and test splits.
    X arrays are reshaped to 2D and scaled using Z-Score Normalization.
    y arrays are scaled using a separate scaler fit on y_train.
    Parameters:
    X_train (np.ndarray): A numpy array containing the training features.
    X_val (np.ndarray): A numpy array containing the validation features.
    X_test (np.ndarray): A numpy array containing the test features.
    y_train (np.ndarray): A numpy array containing the training target variable.
    y_val (np.ndarray): A numpy array containing the validation target variable.
    y_test (np.ndarray): A numpy array containing the test target variable.
    Returns:
    tuple: A tuple containing the normalized X and y arrays, the X scaler and the y scaler.
    """
    X_train_reshape = X_train.reshape(-1, X_train.shape[-1])
    X_val_reshape = X_val.reshape(-1, X_train.shape[-1])
    X_test_reshape = X_test.reshape(-1, X_train.shape[-1])
    x_scaler = StandardScaler()
    x_scaler.fit(X_train_reshape)
    X_train_scaled = x_scaler.transform(X_train_reshape).reshape(X_train.shape)
    X_val_scaled = x_scaler.transform(X_val_reshape).reshape(X_val.shape)
    X_test_scaled = x_scaler.transform(X_test_reshape).reshape(X_test.shape)

    y_scaler = StandardScaler()
    y_scaler.fit(y_train.reshape(-1, 1))
    y_train_scaled = y_scaler.transform(y_train.reshape(-1, 1)).flatten()
    y_val_scaled = y_scaler.transform(y_val.reshape(-1, 1)).flatten()
    y_test_scaled = y_scaler.transform(y_test.reshape(-1, 1)).flatten()

    return X_train_scaled, X_val_scaled, X_test_scaled, y_train_scaled, y_val_scaled, y_test_scaled, x_scaler, y_scaler
