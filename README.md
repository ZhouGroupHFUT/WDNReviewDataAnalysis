# WDNReviewDataAnalysis

Dataset and analysis pipeline for a systematic literature review on **deep learning in water supply systems** (DLInWSS), focused on **water distribution networks (WDNs)**. This repository contains the publication metadata (62,442 records, 1951–2026) and the code used to automatically score each paper's relevance to water distribution networks and classify its research problem and method using the DeepSeek large language model (LLM).

## Repository Structure

```
WDNReviewDataAnalysis/
├── 01_DeepSeekGetScore.ipynb   # Main pipeline: LLM-based relevance scoring & classification
├── system_prompt.txt           # System prompt (scoring rubric & taxonomies) used by the notebook
├── merge_by_year.py            # Merges the per-year pickle files back into single files
├── data/
│   ├── raw_df/                 # Raw publication metadata, split by publication year (69 files)
│   └── handle_df/              # LLM-scored data, split by publication year (69 files)
└── README.md
```

## Code Files

### `01_DeepSeekGetScore.ipynb`

The main analysis pipeline. For every publication, it sends the title, abstract, and keywords to the DeepSeek API and extracts:

- **`Score`** — relevance to water distribution networks, on a 0–10 scale (0 = excluded topic, e.g., wastewater, hydrology, energy systems; 10 = core WDN study).
- **`Problem`** — research problem category (e.g., `Leakage`, `Calibration`, `Partition`, `Forecasting`, `WaterQuality`, `Review`).
- **`Method`** — hierarchical research method category (e.g., `GNN`, `DRL`, `PINN`, `SBF`, `MachineLearning`, `PhysicalModel`).

Key features:

- **Reliable JSON output** — uses the JSON output mode with automatic fallback to normal mode and robust JSON parsing (handles code fences and empty responses).
- **Retry logic** — up to 5 attempts per paper with exponential backoff; failed papers stay unscored (`NaN`) and are retried automatically on the next run.
- **Concurrency & rate limiting** — 10 concurrent threads with a configurable requests-per-minute cap (`REQUESTS_PER_MINUTE`).
- **Cost tracking** — token-based cost estimation (CNY) for `deepseek-v4-pro` / `deepseek-v4-flash`, including promotional pricing.
- **Checkpoint & resume** — progress is saved to `data/handle_df.pkl` every 100 papers; re-running the notebook only processes unscored entries.

Configuration is at the top of the notebook:

- `API_KEY` — read from the `DEEPSEEK_API_KEY` environment variable, or set directly in the cell.
- `MODEL` — `deepseek-v4-pro` (default) or `deepseek-v4-flash`.
- `MAX_WORKERS`, `REQUESTS_PER_MINUTE`, `CHECKPOINT_EVERY`.

### `system_prompt.txt`

The system prompt used by the scoring notebook. It defines:

- The scope of water distribution network research.
- Excluded topic areas (score 0).
- The 0–10 scoring criteria with few-shot examples.
- The research problem and method taxonomies.

### `merge_by_year.py`

Merges the per-year files in `data/handle_df/` and `data/raw_df/` back into single pandas pickle files (`data/handle_df.pkl` and `data/raw_df.pkl`). The original row order is restored exactly using the `_orig_order` helper column (which is then removed automatically).

```bash
python merge_by_year.py
```

## Data Files

All data files are **pandas pickle files** (`.pkl`, readable with `pandas.read_pickle`). To keep individual files small enough for upload, each dataset is split into **69 files by publication year** (1951–2026).

### `data/raw_df/` — raw publication metadata

62,442 records retrieved from literature databases, before LLM scoring.

| Column     | Description                       |
| ---------- | --------------------------------- |
| `Year`     | Publication year                  |
| `Title`    | Paper title                       |
| `Journal`  | Journal / source                  |
| `Keywords` | Author keywords                   |
| `Abstract` | Abstract text                     |
| `_orig_order` | Internal helper column (see note below) |

### `data/handle_df/` — LLM-scored data

62,442 records produced by the scoring notebook (`raw_df` + LLM annotations).

| Column     | Description                                    |
| ---------- | ---------------------------------------------- |
| `Year`     | Publication year                               |
| `Title`    | Paper title                                    |
| `Journal`  | Journal / source                               |
| `Keywords` | Author keywords                                |
| `Abstract` | Abstract text                                  |
| `Score`    | Relevance score (0–10); `NaN` = not scored yet |
| `Problem`  | Research problem category (for `Score` ≥ 6)    |
| `Method`   | Research method category (for `Score` ≥ 6)     |
| `_orig_order` | Internal helper column (see note below)     |

> **Note on `_orig_order`:** this integer column records the original row position of each record and is used by `merge_by_year.py` to restore the exact row order after merging. It is removed automatically during merging.

## Getting Started

### Requirements

- Python 3.8+
- `pandas`
- `openai`
- `tqdm`

```bash
pip install pandas openai tqdm
```

### Running the scoring pipeline

1. Set your API key:

   ```bash
   # Windows (PowerShell)
   $env:DEEPSEEK_API_KEY = "sk-..."
   # Linux / macOS
   export DEEPSEEK_API_KEY="sk-..."
   ```

2. Open `01_DeepSeekGetScore.ipynb` and run the cells.

3. To reconstruct the full single-file datasets after downloading the split files:

   ```bash
   python merge_by_year.py
   ```

## Notes

- The relevance score (0–10), problem categories, and method categories follow the rubric defined in `system_prompt.txt`.
- Papers that failed after all retry attempts remain unscored (`NaN` in `Score`); re-run the notebook to retry them.
