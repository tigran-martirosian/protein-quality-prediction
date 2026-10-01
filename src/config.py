"""Constants and paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SAMPLE_CSV = DATA_DIR / "sample" / "foods_sample.csv"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"
SQL_SCHEMA = ROOT / "sql" / "schema.sql"
DEFAULT_SQLITE_PATH = PROCESSED_DIR / "protein.db"

# FAO/WHO 2007 adult reference pattern, mg amino acid per g protein.
FAO_WHO_REFERENCE = {
    "histidine":  15.0,
    "isoleucine": 30.0,
    "leucine":    59.0,
    "lysine":     45.0,
    "saa":        22.0,
    "aaa":        38.0,
    "threonine":  23.0,
    "tryptophan":  6.0,
    "valine":     39.0,
}

ESSENTIAL_AA_FEATURES = [
    "histidine_per_g", "isoleucine_per_g", "leucine_per_g", "lysine_per_g",
    "saa_per_g", "aaa_per_g", "threonine_per_g", "tryptophan_per_g",
    "valine_per_g",
]

RAW_AA_COLUMNS = [
    "histidine_mg", "isoleucine_mg", "leucine_mg", "lysine_mg",
    "methionine_mg", "cysteine_mg", "phenylalanine_mg", "tyrosine_mg",
    "threonine_mg", "tryptophan_mg", "valine_mg",
]

COMPLETENESS_THRESHOLD = 1.0

# True ileal digestibility per category (FAO/WHO 2013 DIAAS literature).
CATEGORY_DIGESTIBILITY = {
    "Dairy_Eggs": 0.97,
    "Meat":       0.94,
    "Seafood":    0.94,
    "Legumes":    0.82,
    "Grains":     0.82,
    "Nuts_Seeds": 0.80,
    "Vegetables": 0.70,
    "Other":      0.85,
}
DEFAULT_DIGESTIBILITY = 0.80
