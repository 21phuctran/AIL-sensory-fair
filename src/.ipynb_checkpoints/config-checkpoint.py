from pathlib import Path

CATEGORY = "Amazon_Fashion"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

DB_PATH = DATA_DIR / "ail_sensory.duckdb"

FULL_REVIEWS_PATH = RAW_DIR / "Amazon_Fashion.jsonl"
FULL_META_PATH = RAW_DIR / "meta_Amazon_Fashion.jsonl"

# Change this when you want to use the full dataset instead of a dev sample. 
USE_DEV_SAMPLE = False
DEV_SAMPLE_SIZE = 20_000

REVIEWS_DEV_PARQUET = INTERIM_DIR / f"{CATEGORY}_reviews_dev_sample.parquet"
META_DEV_PARQUET = INTERIM_DIR / f"{CATEGORY}_metadata_dev_matched.parquet"

JOINED_PARQUET = PROCESSED_DIR / f"{CATEGORY}_joined_reviews.parquet"
LABELED_PARQUET = PROCESSED_DIR / f"{CATEGORY}_weak_labeled_reviews.parquet"
PRODUCT_SCORES_CSV = PROCESSED_DIR / f"{CATEGORY}_product_sensory_scores.csv"