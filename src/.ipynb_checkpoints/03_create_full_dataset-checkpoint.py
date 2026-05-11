import json
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from config import (
    FULL_REVIEWS_PATH,
    FULL_META_PATH,
    PROCESSED_DIR,
)

JOINED_FULL_PARQUET = PROCESSED_DIR / "Amazon_Fashion_joined_reviews.parquet"

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
    if value is None:
        return None

    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)

    return value


def read_all_reviews():
    rows = []

    print("Reading all review rows from:")
    print(FULL_REVIEWS_PATH)

    with open(FULL_REVIEWS_PATH, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            row = json.loads(line)

            cleaned_row = {
                col: json_safe(row.get(col))
                for col in REVIEW_KEEP_COLS
            }

            rows.append(cleaned_row)

    df_reviews = pd.DataFrame(rows)

    df_reviews["parent_asin"] = df_reviews["parent_asin"].astype(str).str.strip()

    df_reviews = df_reviews.rename(columns={
        "title": "review_title",
        "text": "review_text",
    })

    return df_reviews


def read_matching_metadata(parent_asins):
    rows = []
    found_parent_asins = set()

    print("\nReading metadata rows and keeping matching parent_asin values...")
    print(FULL_META_PATH)

    with open(FULL_META_PATH, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            row = json.loads(line)
            parent = str(row.get("parent_asin")).strip()

            if parent in parent_asins:
                cleaned_row = {
                    col: json_safe(row.get(col))
                    for col in META_KEEP_COLS
                }

                rows.append(cleaned_row)
                found_parent_asins.add(parent)

    df_meta = pd.DataFrame(rows)

    if len(df_meta) > 0:
        df_meta["parent_asin"] = df_meta["parent_asin"].astype(str).str.strip()

        df_meta = df_meta.rename(columns={
            "title": "product_title",
        })

        # Avoid duplicate metadata rows causing merge explosion
        df_meta = df_meta.drop_duplicates(subset=["parent_asin"])

    missing_parent_asins = parent_asins - found_parent_asins

    return df_meta, found_parent_asins, missing_parent_asins


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_reviews = read_all_reviews()

    parent_asins = set(df_reviews["parent_asin"].dropna().unique())

    print("\nFull review summary:")
    print(f"Review rows: {len(df_reviews):,}")
    print(f"Unique parent_asin values: {len(parent_asins):,}")
    print(f"Review columns: {df_reviews.columns.tolist()}")

    df_meta, found_parent_asins, missing_parent_asins = read_matching_metadata(parent_asins)

    print("\nMetadata match summary:")
    print(f"Metadata rows found: {len(df_meta):,}")
    print(f"Matched parent_asin values: {len(found_parent_asins):,}")
    print(f"Missing parent_asin values: {len(missing_parent_asins):,}")

    print("\nMerging reviews with metadata...")

    combined = df_reviews.merge(
        df_meta,
        on="parent_asin",
        how="left"
    )

    final_cols = [
        "rating",
        "review_title",
        "review_text",
        "asin",
        "parent_asin",
        "user_id",
        "timestamp",
        "helpful_vote",
        "verified_purchase",
        "product_title",
        "main_category",
        "average_rating",
        "rating_number",
        "features",
        "description",
        "price",
        "store",
        "categories",
        "details",
    ]

    combined = combined[final_cols]

    print("\nCombined summary:")
    print(f"Combined rows: {len(combined):,}")
    print(f"Combined columns: {combined.columns.tolist()}")
    print(f"Missing product titles: {combined['product_title'].isna().sum():,}")

    combined.to_parquet(JOINED_FULL_PARQUET, index=False)

    print("\nSaved full joined dataset to:")
    print(JOINED_FULL_PARQUET)


if __name__ == "__main__":
    main()