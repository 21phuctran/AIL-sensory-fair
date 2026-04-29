import duckdb

from config import (
    DB_PATH,
    REVIEWS_DEV_PARQUET,
    META_DEV_PARQUET,
    JOINED_PARQUET,
    PROCESSED_DIR,
    USE_DEV_SAMPLE,
)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Connecting to DuckDB database:")
    print(DB_PATH)

    con = duckdb.connect(str(DB_PATH))

    if USE_DEV_SAMPLE:
        print("\nUsing DEV sample...")

        print("Creating reviews table from dev reviews Parquet...")
        con.execute(
            """
            CREATE OR REPLACE TABLE reviews AS
            SELECT *
            FROM read_parquet(?)
            """,
            [str(REVIEWS_DEV_PARQUET)],
        )

        print("Creating product_metadata table from dev metadata Parquet...")
        con.execute(
            """
            CREATE OR REPLACE TABLE product_metadata AS
            SELECT *
            FROM read_parquet(?)
            """,
            [str(META_DEV_PARQUET)],
        )

        print("Creating joined_reviews table from dev tables...")
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

    else:
        print("\nUsing FULL dataset...")

        print("Creating joined_reviews table from full joined Parquet...")
        con.execute(
            """
            CREATE OR REPLACE TABLE joined_reviews AS
            SELECT *
            FROM read_parquet(?)
            """,
            [str(JOINED_PARQUET)],
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

    con.close()

    print("\nDone. DuckDB now contains the joined_reviews table.")


if __name__ == "__main__":
    main()