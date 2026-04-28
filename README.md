# AIL-sensory-fair

This project uses the Amazon Reviews 2023 `Amazon_Fashion` dataset to explore whether customer reviews and product metadata can help identify sensory-risk signals for SensoryFair product screening.

Check findings.md for more details

## Project Structure

| Directory / File | Description | Details |
|---|---|---|
| `src/` | Main Python pipeline code. | Contains scripts for checking local data files, creating dev samples, building DuckDB tables, joining reviews with metadata, and later creating sensory-risk labels. |
| `src/config.py` | Central project settings file. | Stores dataset category, file paths, DuckDB path, dev sample size, and output paths so all scripts use the same settings. |
| `src/00_check_local_files.py` | Raw data sanity check script. | Confirms that the local `.jsonl` files exist, can be read, and contain expected columns such as `rating`, `review_text`, `parent_asin`, and product metadata fields. |
| `src/01_create_dev_sample.py` | Dev sample creation script. | Creates a smaller review sample and matching product metadata file from the full downloaded Amazon Fashion dataset. Used for faster debugging and learning. |
| `src/02_build_duckdb.py` | DuckDB database construction script. | Loads the dev sample Parquet files into DuckDB, creates review and metadata tables, joins them using `parent_asin`, and exports a joined Parquet file. |
| `data/` | Local data storage. | Stores raw downloaded files, intermediate Parquet files, processed joined data, and the local DuckDB database. Large data files should not be pushed to GitHub. |
| `data/raw/` | Original downloaded Amazon files. | Contains files such as `Amazon_Fashion.jsonl` and `meta_Amazon_Fashion.jsonl`. These are the untouched source files. |
| `data/interim/` | Intermediate working files. | Contains dev sample Parquet files such as `Amazon_Fashion_reviews_dev_sample.parquet` and `Amazon_Fashion_metadata_dev_matched.parquet`. |
| `data/processed/` | Cleaned analysis-ready files. | Contains joined review + metadata files and later weak-labeled review files or product-level sensory score files. |
| `data/ail_sensory.duckdb` | Local DuckDB database. | Stores SQL tables for reviews, product metadata, joined reviews, and later labeled data. Used for faster joins, filtering, and aggregation. |
| `notebooks/` | Exploratory data analysis notebooks. | Used for missing-value analysis, rating distribution, review length analysis, reviews-per-product analysis, sensory keyword exploration, and manual inspection. |
| `notebooks/01_eda_joined_reviews.ipynb` | Main EDA notebook. | Explores the joined Amazon Fashion dev sample before weak labeling or ML. Used to decide which columns and keywords are reliable. |
| `outputs/` | Exported analysis outputs. | Stores charts, summary tables, validation samples, and future reports for AIL review. |
| `models/` | Saved ML models. | Reserved for later baseline models such as TF-IDF + Logistic Regression or transformer-based classifiers. Not used yet. |
| `dashboard/` | Dashboard files. | Reserved for Power BI or other dashboard assets showing product-level sensory-risk summaries. |
| `requirements.txt` | Python dependencies. | Lists required packages such as `pandas`, `duckdb`, `pyarrow`, `tqdm`, `scikit-learn`, and `jupyter`. |
| `README.md` | Project documentation. | Explains the project goal, structure, workflow, and current status. |

## Current Workflow

```text
Raw Amazon Fashion JSONL files
        ↓
Sanity check local files
        ↓
Create dev sample
        ↓
Build DuckDB tables
        ↓
Join reviews with product metadata
        ↓
Run EDA (Current Step)
        ↓
Create weak sensory labels
        ↓
Create product-level scores
        ↓
Build dashboard / ML baseline later
```

## Setup
This project uses uv for package management.

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the repo and install dependencies

```bash
git clone https://github.com/21phuctran/AIL-sensory-fair.git
cd AIL-sensory-fair
uv sync
```

This creates a `.venv/` with all pinned dependencies from `uv.lock`.

### 3. Download the data

1. https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
2. Go to Grouped by Category section
3. On Amazon_Fashion, download review and meta
4. Extract and Place them in `AIL-sensory-fair/data/raw`

Run all three files in src at the start for initial dataset