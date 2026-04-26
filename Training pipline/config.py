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

PRICE_COLS = ["Open", "High", "Low", "Close"]

WINDOWS = [5, 10, 20, 60]

# --- Model hyperparameters ---
BATCH_SIZE = 32
EPOCHS = 50
PATIENCE = 15

UNITS = 64
FILTERS = 64
NUM_HEADS = 4
KEY_DIM = 64
FF_DIM = 32

N_ESTIMATORS = 300
LEARNING_RATE = 0.3
MAX_DEPTH = 8
EARLY_STOPPING_ROUNDS = 10
RANDOM_STATE = 42
MIN_SAMPLE_SPLIT = 2
MIN_SAMPLE_LEAF = 1

# --- Pipeline Control ---
RUN_INGESTION = False
RUN_FEATURE_ENGINEERING = False
RUN_TRAINING = True
MODELS_TO_RUN = ['xgb', 'lgbm', 'rf', 'cnn', 'lstm', 'transformer']
WINDOWS_TO_RUN = [5, 10, 20, 60]

# --- Sentiment Control ---
# USE_SENTIMENT = True  : runs both config A (price-only) and config B (price+sentiment)
# USE_SENTIMENT = False : runs config A only
USE_SENTIMENT = True

# Directory containing per-ticker sentiment CSVs (e.g. 1023_KL_title.csv)
SENTIMENT_DIR = 'data/sentiment/title'

# How to fill no-news trading days:
#   'ffill'   - carry forward the last known sentiment signal
#   'neutral' - fill with a flat neutral baseline (score=0, prob=1/3 each)
SENTIMENT_FILL_STRATEGY = 'ffill'

# --- Data Paths ---
CLEANED_DATA_PATH = 'data/cleaned_data.parquet'
FEATURED_DATA_PATH = 'data/featured_data_{window}d.parquet'
FEATURED_SENTIMENT_DATA_PATH = 'data/featured_sentiment_data_{window}d.parquet'
