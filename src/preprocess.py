"""Drop foods with missing/low protein and fill amino acid NaNs with 0."""
from .config import RAW_AA_COLUMNS


def preprocess(df, min_protein_g=1.0):
    df = df.copy()
    df = df[df["protein_g"].notna()]
    df = df[df["protein_g"] >= min_protein_g]
    for col in RAW_AA_COLUMNS:
        if col in df.columns:
            df[col] = df[col].fillna(0.0).clip(lower=0.0)
    return df.reset_index(drop=True)
