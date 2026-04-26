from sklearn.ensemble import RandomForestRegressor as RF
from config import N_ESTIMATORS, MAX_DEPTH, RANDOM_STATE, MIN_SAMPLE_SPLIT, MIN_SAMPLE_LEAF


def build_rf() -> RF:
    """
    This function builds and returns a compiled RandomForestRegressor model.
    Returns:
    RandomForestRegressor: A compiled RandomForestRegressor model.
    """

    model = RF(
        n_estimators=N_ESTIMATORS,
        min_samples_leaf=MIN_SAMPLE_LEAF,
        min_samples_split=MIN_SAMPLE_SPLIT,
        random_state=RANDOM_STATE,
        max_depth=MAX_DEPTH,

    )
    return model
