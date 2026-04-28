import duckdb

from config import (
    DB_PATH,
    REVIEWS_DEV_PARQUET,
    META_DEV_PARQUET,
    JOINED_PARQUET,
    PROCESSED_DIR,
)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Connecting to DuckDB database:")
    print(DB_PATH)

    con = duckdb.connect(str(DB_PATH))

    print("\nCreating reviews table from Parquet...")

    con.execute(
        """
        CREATE OR REPLACE TABLE reviews AS
        SELECT *
        FROM read_parquet(?)
        """,
        [str(REVIEWS_DEV_PARQUET)],
    )

    print("Creating product_metadata table from Parquet...")

    con.execute(
        """
        CREATE OR REPLACE TABLE product_metadata AS
        SELECT *
        FROM read_parquet(?)
        """,
        [str(META_DEV_PARQUET)],
    )

    print("Creating joined_reviews table...")

    con.execute(
        """
        CREATE OR REPLACE TABLE joined_reviews AS
        SELECT
            r.rating,
            r.title AS review_title,
            r.text AS review_text,
            r.asin,
            r.parent_asin,
            r.user_id,
            r.timestamp,
            r.helpful_vote,
            r.verified_purchase,

            m.title AS product_title,
            m.main_category,
            m.average_rating,
            m.rating_number,
            m.features,
            m.description,
            m.price,
            m.store,
            m.categories,
            m.details

        FROM reviews r
        LEFT JOIN product_metadata m
        ON r.parent_asin = m.parent_asin
        """
    )

    print("\nJoin summary:")

    summary = con.execute(
        """
        SELECT
            COUNT(*) AS total_review_rows,
            COUNT(product_title) AS rows_with_product_metadata,
            COUNT(*) - COUNT(product_title) AS rows_missing_product_metadata,
            COUNT(DISTINCT parent_asin) AS unique_products
        FROM joined_reviews
        """
    ).fetchdf()

    print(summary)

    print("\nPreview of joined data:")

    preview = con.execute(
        """
        SELECT
            product_title,
            review_title,
            review_text,
            rating,
            price,
            store
        FROM joined_reviews
        LIMIT 5
        """
    ).fetchdf()

    print(preview)

    print("\nSaving joined table to Parquet...")

    # Convert Windows backslashes to forward slashes for safer DuckDB file writing.
    joined_path = str(JOINED_PARQUET).replace("\\", "/")

    con.execute(
        f"""
        COPY joined_reviews
        TO '{joined_path}'
        (FORMAT PARQUET)
        """
    )

    print(f"\nSaved joined Parquet file to:")
    print(JOINED_PARQUET)

    con.close()

    print("\nDone. Next step will be creating weak sensory labels.")


if __name__ == "__main__":
    main()