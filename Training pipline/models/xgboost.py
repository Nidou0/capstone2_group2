import xgboost as xgb
from config import N_ESTIMATORS, LEARNING_RATE, MAX_DEPTH, RANDOM_STATE, EARLY_STOPPING_ROUNDS


def build_xgb() -> xgb.XGBRegressor:
    """
    This function builds and returns a compiled XGBRegressor model.
    Returns:
    xgb.XGBRegressor: A compiled XGBRegressor model.
    """

    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        early_stopping_rounds=EARLY_STOPPING_ROUNDS
    )
    return model
