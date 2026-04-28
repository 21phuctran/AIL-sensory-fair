# Findings: Amazon Fashion Sensory-Risk Data Setup

## Project Goal

Explores whether Amazon Fashion reviews and product metadata can help AIL/SensoryFair identify early sensory-risk signals in products.

The goal is not to create a final autism-safe classifier yet. The current goal is to build a clean data pipeline, understand the dataset, and decide whether the data is useful enough for weak labeling, dashboarding, and later ML work.

## What Was Completed

The full `Amazon_Fashion` review and metadata files were downloaded locally as `.jsonl` files.

A project structure was created with separate folders for source code, raw data, intermediate files, processed files, notebooks, outputs, models, and dashboard work.

A `config.py` file was created to store paths and project settings in one central place. This makes the pipeline easier to update and easier for teammates to understand.

A local sanity check script was created to confirm that the raw review and metadata files exist, can be read, and contain the expected fields.

A 20,000-row dev sample was created from the full Amazon Fashion review file. This sample was used for debugging, learning, and early EDA before running anything on the full dataset.

Product metadata was matched to the review sample using `parent_asin`. The join worked well: all sampled products had matching metadata, with 0 missing `parent_asin` matches.

A DuckDB database was built, and review data was joined with product metadata into one analysis-ready file.

## Why We Used a 20,000-Row Dev Sample

The dev sample was not meant to be the final dataset. It was used to test the pipeline quickly before scaling up.

The sample helped confirm that the files load correctly, the columns are usable, the metadata join works, and the EDA code runs without waiting on the full dataset each time.

The full dataset should still be used later for real conclusions and product-level scoring.

## Key EDA Findings

Most of the EDA so far was done on the 20,000-row dev sample. The dev sample was used to quickly test the pipeline, inspect the data, and understand whether the fields are useful before running full-dataset analysis.

The important review fields in the dev sample are complete and usable. These include `review_text`, `review_title`, `rating`, `asin`, `parent_asin`, `timestamp`, `helpful_vote`, and `verified_purchase`.

The metadata join worked correctly in the dev sample. Product metadata was successfully matched to reviews using `parent_asin`, with 0 missing metadata matches. After joining, fields such as `product_title`, `main_category`, `average_rating`, `rating_number`, `features`, `details`, and `store` were available.

The `categories` column is not useful. Unlike the other findings, this was checked on the full Amazon Fashion metadata file, not just the dev sample. The raw metadata showed `categories = None` across all checked rows, meaning this is a data issue and not a problem with our code. We should drop or ignore `categories`.

The `description` column was mostly missing or empty in the dev sample, so it should not be relied on for the first version.

The `price` column had high missingness in the dev sample, so it should not be used in the first version.

The `details` column looks highly useful in the dev sample. Around 97% of products in the dev sample had usable details. Some detail fields are not useful, such as package dimensions or date first available, but other fields may help with product context, such as material, color, size, department, style, pattern, and age range.

The `features` column is useful when present, but it was missing for around 40% of products in the dev sample. It can provide useful product context like compression, breathable fabric, lightweight material, hypoallergenic claims, and stretch, but it should be treated as optional.

The rating distribution in the dev sample was heavily positive, with many 5-star reviews. This suggests sensory complaints should not only be searched in low-rated reviews. A review can be positive overall while still mentioning a sensory issue.

The review text length in the dev sample appears usable for early sensory keyword exploration. Many reviews are short, but enough reviews have meaningful text for identifying terms like itchy, scratchy, tight, seams, smell, breathable, and compression.

The 20,000-row dev sample is weak for product-level scoring because most products in the sample only have one review. Product-level risk scores from this sample would be unstable and should not be treated as final.

## Current Decision

For version 1, we should focus on these fields:

- `review_text`
- `review_title`
- `product_title`
- `parent_asin`
- `rating`
- `verified_purchase`
- `helpful_vote`
- `details`
- `features`

We should ignore or drop these fields for version 1:

- `categories`
- `description`
- `price`

The strongest evidence should come from customer reviews, not product marketing descriptions.

## Main Risk

The biggest risk is creating weak labels too early without checking whether the keywords are actually meaningful.

For example, the word `tight` may describe a real sensory issue, such as a tight waistband, but it could also describe something unrelated, such as tight packaging. This is why sensory keyword exploration and manual review are needed before training any model.

## Next Plan

The next step is to run targeted EDA on the full Amazon Fashion dataset using DuckDB, not pandas-only processing. This should include full-dataset rating distribution, review length distribution, reviews per product, missing-value checks, and usable metadata checks.

After that, we should do sensory term exploration across the full review text. Terms to inspect include itchy, scratchy, rough, tight, too tight, seam, tag, smell, odor, hot, sweaty, breathable, compression, pressure, stretchy, and stiff.

Then we should manually inspect examples for each term to decide which words are reliable enough for weak labels.

After that, we can create weak sensory-risk labels and test them on a sample of flagged and unflagged reviews.

Only after label quality is checked should we move toward product-level sensory-risk scoring or baseline ML modeling.

