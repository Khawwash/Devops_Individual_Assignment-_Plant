from __future__ import annotations
import argparse
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
import kagglehub
import pandas as pd
import re 

pd.options.mode.copy_on_write = True

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DATASETS: Dict[str, Dict[str, object]] = {
    "plant_health": {
        "ref": "ziya07/plant-health-data",
        "preferred_files": [
            "Plant Health Data.csv",
            "Plant Health Dataset.csv",
            "Plant_Health_data.csv",
        ],
    },
    "plant_growth": {
        "ref": "gorororororo23/plant-growth-data-classification",
        "preferred_files": [
            "Plant Growth Data.csv",
            "Plant_growth_data.csv",
            "dataset.csv",
        ],
    },
    "auto_irrigation": {
        "ref": "harshilpatel355/autoirrigationdata",
        "preferred_files": [
            "AutoIrrigationData.csv",
            "auto_irrigation_data.csv",
        ],
    },
    "crop_water_requirement": {
        "ref": "prateekkkumar/crop-water-requirement",
        "preferred_files": [
            "Crop Water Requirement.csv",
            "crop_water_requirement.csv",
        ],
    },
    "watering_prediction": {
        "ref": "nelakurthisudheer/dataset-for-predicting-watering-the-plants",
        "preferred_files": [
            "PlantWateringDataset.csv",
            "watering_data.csv",
            "watering.csv",
        ],
    },
}

KEY_PRIORITY: Sequence[Tuple[str, ...]] = (
    ("plant_id", "date"),
    ("plant_id", "timestamp"),
    ("plant_id",),
    ("plant", "date"),
    ("plant", "timestamp"),
    ("plant",),
    ("species", "date"),
    ("species",),
    ("plant_name", "date"),
    ("plant_name",),
    ("id", "date"),
    ("id",),
)


def download_datasets(config: Dict[str, Dict[str, object]]) -> Dict[str, Path]:
    paths: Dict[str, Path] = {}
    for name, info in config.items():
        ref = info["ref"]
        path = Path(kagglehub.dataset_download(ref))  # type: ignore[arg-type]
        paths[name] = path
        logger.info("Downloaded %s dataset to %s", name, path)
    return paths


def choose_csv(base: Path, preferred: Iterable[str]) -> Path:
    # pick declared file if present, otherwise first CSV we find
    preferred_set = {p.lower() for p in preferred}
    for candidate in base.rglob("*.csv"):
        if candidate.name.lower() in preferred_set:
            return candidate
    csv_files = sorted(base.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {base}")
    return csv_files[0]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str).str.strip()
    df = df.drop_duplicates().reset_index(drop=True)
    return df

import re

RANGE_RE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)$")

def _coerce_numeric(series: pd.Series) -> pd.Series:
    def parse(value):
        if pd.isna(value):
            return pd.NA
        text = str(value).strip()
        if text == "":
            return pd.NA
        match = RANGE_RE.match(text)
        if match:
            lo, hi = map(float, match.groups())
            return (lo + hi) / 2
        if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
            return float(text)
        return text  # leave non-numeric as-is
    return series.map(parse)

def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = _coerce_numeric(df[col])
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    return df



def load_clean_dataset(name: str, base_path: Path, info: Dict[str, object]) -> pd.DataFrame:
    csv_path = choose_csv(base_path, info.get("preferred_files", []))
    logger.info("Loading %s from %s", name, csv_path.name)
    df = pd.read_csv(csv_path)
    df = standardize_columns(df)
    df = convert_types(df)
    df["source_dataset"] = name
    return df


def find_merge_keys(left_cols: Iterable[str], right_cols: Iterable[str]) -> Tuple[str, ...] | None:
    left_set = set(left_cols)
    right_set = set(right_cols)
    for combo in KEY_PRIORITY:
        if set(combo).issubset(left_set) and set(combo).issubset(right_set):
            return combo
    return None


def merge_dataframes(frames: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    items = list(frames.items())
    if not items:
        raise ValueError("No datasets were loaded.")
    unified_name, unified_df = items[0]
    logger.info("Using %s as the base table", unified_name)
    for name, df in items[1:]:
        keys = find_merge_keys(unified_df.columns, df.columns)
        if keys:
            logger.info("Merging %s on keys %s", name, keys)
            unified_df = unified_df.merge(df, on=list(keys), how="outer", suffixes=("", f"_{name}"))
        else:
            logger.warning("No common keys found with %s; concatenating rows instead", name)
            unified_df = pd.concat([unified_df, df], ignore_index=True, sort=False)
    unified_df = unified_df.sort_index().reset_index(drop=True)
    return unified_df


def summarize(df: pd.DataFrame) -> None:
    logger.info("Unified dataset shape: %s", df.shape)
    null_pct = df.isna().mean().sort_values(ascending=False)
    missing = null_pct[null_pct > 0].head(10)
    if not missing.empty:
        logger.info("Top columns with missing values:\n%s", missing.to_string())
    else:
        logger.info("No missing values detected.")


def persist(df: pd.DataFrame, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".parquet":
        df.to_parquet(output, index=False)
    else:
        df.to_csv(output, index=False)
    logger.info("Unified dataset saved to %s", output)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download, clean, and merge plant datasets.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/unified_plants.parquet"),
        help="Destination file (.csv or .parquet).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download_paths = download_datasets(DATASETS)
    frames = {
        name: load_clean_dataset(name, base_path, DATASETS[name])
        for name, base_path in download_paths.items()
    }
    unified = merge_dataframes(frames)
    summarize(unified)
    persist(unified, args.output)


if __name__ == "__main__":
    main()
