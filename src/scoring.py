"""Amino Acid Score and PDCAAS-style Protein Quality Score.

PQS = digestibility * min(AAS), where AAS for each essential amino acid is
the food's mg/g-protein divided by the FAO/WHO 2007 reference value.
"""
from .config import (
    FAO_WHO_REFERENCE,
    COMPLETENESS_THRESHOLD,
    CATEGORY_DIGESTIBILITY,
    DEFAULT_DIGESTIBILITY,
)

FEATURE_TO_REF = {
    "histidine_per_g":  "histidine",
    "isoleucine_per_g": "isoleucine",
    "leucine_per_g":    "leucine",
    "lysine_per_g":     "lysine",
    "saa_per_g":        "saa",
    "aaa_per_g":        "aaa",
    "threonine_per_g":  "threonine",
    "tryptophan_per_g": "tryptophan",
    "valine_per_g":     "valine",
}


def add_amino_acid_scores(df):
    df = df.copy()
    for feat, key in FEATURE_TO_REF.items():
        df[f"AAS_{key}"] = df[feat] / FAO_WHO_REFERENCE[key]
    return df


def add_digestibility(df):
    df = df.copy()
    df["digestibility"] = (
        df["category_name"]
          .map(CATEGORY_DIGESTIBILITY)
          .fillna(DEFAULT_DIGESTIBILITY)
    )
    return df


def add_protein_quality_score(df):
    df = df.copy()
    aas_cols = [f"AAS_{k}" for k in FEATURE_TO_REF.values()]
    df["AAS_min"] = df[aas_cols].min(axis=1)
    df["limiting_amino_acid"] = df[aas_cols].idxmin(axis=1).str.replace("AAS_", "", regex=False)
    df["PQS"] = df["AAS_min"] * df["digestibility"]
    df["is_complete"] = (df["PQS"] >= COMPLETENESS_THRESHOLD).astype(int)
    return df


def compute_all(df):
    df = add_amino_acid_scores(df)
    df = add_digestibility(df)
    df = add_protein_quality_score(df)
    return df
