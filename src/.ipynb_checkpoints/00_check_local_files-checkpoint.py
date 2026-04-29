import json

from config import FULL_REVIEWS_PATH, FULL_META_PATH


EXPECTED_REVIEW_KEYS = {
    "rating",
    "title",
    "text",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
}

EXPECTED_META_KEYS = {
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
}


def check_jsonl_file(path, label, expected_keys, num_rows_to_check=100):
    print("=" * 80)
    print(f"Checking: {label}")
    print(f"Path: {path}")

    if not path.exists():
        print("FAILED: File does not exist.")
        return

    size_mb = path.stat().st_size / (1024 * 1024)
    print("File exists.")
    print(f"File size: {size_mb:.2f} MB")

    all_seen_keys = set()
    row_count = 0
    bad_json_rows = 0
    rows_missing_parent_asin = 0

    first_row = None

    with open(path, "r", encoding="utf-8") as f:
        for i in range(num_rows_to_check):
            line = f.readline()

            if not line:
                break

            row_count += 1

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                bad_json_rows += 1
                continue

            if first_row is None:
                first_row = row

            all_seen_keys.update(row.keys())

            if "parent_asin" not in row or row["parent_asin"] in [None, ""]:
                rows_missing_parent_asin += 1

    missing_expected_keys = expected_keys - all_seen_keys
    extra_keys = all_seen_keys - expected_keys

    print(f"\nRows checked: {row_count}")
    print(f"Bad JSON rows: {bad_json_rows}")
    print(f"Rows missing parent_asin: {rows_missing_parent_asin}")

    print("\nExpected keys:")
    print(sorted(expected_keys))

    print("\nKeys found in checked rows:")
    print(sorted(all_seen_keys))

    if missing_expected_keys:
        print("\nFAILED: Missing expected keys:")
        print(sorted(missing_expected_keys))
    else:
        print("\nPASSED: All expected keys were found.")

    if extra_keys:
        print("\nExtra keys found. This is usually okay:")
        print(sorted(extra_keys))

    print("\nFirst row preview:")
    if first_row:
        preview = {k: first_row.get(k) for k in list(first_row.keys())[:8]}
        print(preview)
    else:
        print("No readable rows found.")


check_jsonl_file(
    path=FULL_REVIEWS_PATH,
    label="Amazon Fashion reviews",
    expected_keys=EXPECTED_REVIEW_KEYS,
)

check_jsonl_file(
    path=FULL_META_PATH,
    label="Amazon Fashion metadata",
    expected_keys=EXPECTED_META_KEYS,
)