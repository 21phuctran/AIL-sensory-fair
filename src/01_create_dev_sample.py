import json
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from config import (
    FULL_REVIEWS_PATH,
    FULL_META_PATH,
    INTERIM_DIR,
    DEV_SAMPLE_SIZE,
    REVIEWS_DEV_PARQUET,
    META_DEV_PARQUET,
)


REVIEW_KEEP_COLS = [
    "rating",
    "title",
    "text",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
]

META_KEEP_COLS = [
    "main_category",
    "title",
    "average_rating",
    "rating_number",
    "features",
    "description",
    "price",
    "store",
    "categories",
    "details",
    "parent_asin",
]


def json_safe(value):
    """
    Some metadata fields are lists or dictionaries.
    Parquet can handle many types, but for beginner debugging,
    converting lists/dicts into JSON strings keeps things simpler.
    """
    if value is None:
        return None

    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)

    return value


def read_review_sample():
    """
    Read the first DEV_SAMPLE_SIZE review rows from the local JSONL file.
    """
    rows = []

    print(f"Reading {DEV_SAMPLE_SIZE:,} review rows from:")
    print(FULL_REVIEWS_PATH)

    with open(FULL_REVIEWS_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(tqdm(f, total=DEV_SAMPLE_SIZE)):
            if i >= DEV_SAMPLE_SIZE:
                break

            row = json.loads(line)

            cleaned_row = {
                col: json_safe(row.get(col))
                for col in REVIEW_KEEP_COLS
            }

            rows.append(cleaned_row)

    df_reviews = pd.DataFrame(rows)

    # Make sure parent_asin is a clean string key for joining later.
    df_reviews["parent_asin"] = df_reviews["parent_asin"].astype(str)

    return df_reviews


def read_matching_metadata(parent_asins):
    """
    Read the metadata file line by line and only keep products whose parent_asin
    appears in our review sample.
    """
    rows = []
    found_parent_asins = set()

    print("\nReading metadata rows and keeping only matching parent_asin values...")
    print(FULL_META_PATH)

    with open(FULL_META_PATH, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            row = json.loads(line)
            parent = str(row.get("parent_asin"))

            if parent in parent_asins:
                cleaned_row = {
                    col: json_safe(row.get(col))
                    for col in META_KEEP_COLS
                }

                rows.append(cleaned_row)
                found_parent_asins.add(parent)

            # Stop early if we found metadata for every product in the review sample.
            if found_parent_asins == parent_asins:
                break

    df_meta = pd.DataFrame(rows)

    if len(df_meta) > 0:
        df_meta["parent_asin"] = df_meta["parent_asin"].astype(str)

    missing_parent_asins = parent_asins - found_parent_asins

    return df_meta, found_parent_asins, missing_parent_asins


def main():
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    df_reviews = read_review_sample()

    parent_asins = set(df_reviews["parent_asin"].dropna().unique())

    print("\nReview sample summary:")
    print(f"Review rows: {len(df_reviews):,}")
    print(f"Unique parent_asin values: {len(parent_asins):,}")
    print(f"Review columns: {df_reviews.columns.tolist()}")

    df_reviews.to_parquet(REVIEWS_DEV_PARQUET, index=False)
    print(f"\nSaved review dev sample to:")
    print(REVIEWS_DEV_PARQUET)

    df_meta, found_parent_asins, missing_parent_asins = read_matching_metadata(parent_asins)

    print("\nMetadata match summary:")
    print(f"Metadata rows found: {len(df_meta):,}")
    print(f"Matched parent_asin values: {len(found_parent_asins):,}")
    print(f"Missing parent_asin values: {len(missing_parent_asins):,}")

    if len(df_meta) > 0:
        print(f"Metadata columns: {df_meta.columns.tolist()}")

    df_meta.to_parquet(META_DEV_PARQUET, index=False)
    print(f"\nSaved matched metadata dev sample to:")
    print(META_DEV_PARQUET)

if __name__ == "__main__":
    main()