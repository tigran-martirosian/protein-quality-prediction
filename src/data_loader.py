import pandas as pd
from .config import SAMPLE_CSV, RAW_AA_COLUMNS

REQUIRED = (
    ["food_name", "category_name", "is_animal",
     "protein_g", "fat_g", "carbohydrate_g", "energy_kcal"]
    + RAW_AA_COLUMNS
)


def load_foods(csv_path=None):
    path = csv_path if csv_path else SAMPLE_CSV
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if "food_id" not in df.columns:
        df = df.reset_index(drop=True)
        df.insert(0, "food_id", df.index + 1)
    return df
