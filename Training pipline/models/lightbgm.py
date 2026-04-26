from lightgbm import LGBMRegressor as lbm
from config import N_ESTIMATORS, LEARNING_RATE, MAX_DEPTH, RANDOM_STATE


def build_lbm() -> lbm:
    """
    This function builds and returns a compiled XGBRegressor model.
    Returns:
    xgb.XGBRegressor: A compiled XGBRegressor model.
    """

    model = lbm(
        objective='regression',
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE
    )
    return model
