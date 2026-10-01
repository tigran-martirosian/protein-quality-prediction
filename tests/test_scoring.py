"""Tests for features.py and scoring.py."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.features import add_per_gram_protein_features
from src.scoring  import compute_all
from src.preprocess import preprocess
from src.config   import FAO_WHO_REFERENCE


def make_row(name, protein, **aas_mg):
    row = {
        "food_id": 1, "food_name": name, "category_name": "Test",
        "is_animal": 0, "fdc_id": None,
        "protein_g": protein, "fat_g": 0.0, "carbohydrate_g": 0.0, "energy_kcal": 0.0,
        "histidine_mg": 0, "isoleucine_mg": 0, "leucine_mg": 0, "lysine_mg": 0,
        "methionine_mg": 0, "cysteine_mg": 0,
        "phenylalanine_mg": 0, "tyrosine_mg": 0,
        "threonine_mg": 0, "tryptophan_mg": 0, "valine_mg": 0,
    }
    row.update(aas_mg)
    return row


def test_per_gram_protein_arithmetic():
    df = pd.DataFrame([make_row("food", protein=10.0, lysine_mg=500, leucine_mg=800)])
    out = add_per_gram_protein_features(df)
    assert out.loc[0, "lysine_per_g"] == pytest.approx(50.0)
    assert out.loc[0, "leucine_per_g"] == pytest.approx(80.0)


def test_paired_amino_acids():
    df = pd.DataFrame([make_row("food", protein=10.0,
                                 methionine_mg=100, cysteine_mg=50,
                                 phenylalanine_mg=200, tyrosine_mg=150)])
    out = add_per_gram_protein_features(df)
    assert out.loc[0, "saa_per_g"] == pytest.approx(15.0)
    assert out.loc[0, "aaa_per_g"] == pytest.approx(35.0)


def test_aas_against_reference():
    df = pd.DataFrame([make_row("food", protein=10.0, lysine_mg=450)])
    df = compute_all(add_per_gram_protein_features(df))
    assert df.loc[0, "AAS_lysine"] == pytest.approx(1.0)


def test_pqs_uses_minimum_times_digestibility():
    abundant = 20 * 100
    row = make_row("deficient", protein=10.0,
                   lysine_mg=150, histidine_mg=abundant, isoleucine_mg=abundant,
                   leucine_mg=abundant, methionine_mg=abundant, cysteine_mg=abundant,
                   phenylalanine_mg=abundant, tyrosine_mg=abundant,
                   threonine_mg=abundant, tryptophan_mg=abundant, valine_mg=abundant)
    df = compute_all(add_per_gram_protein_features(pd.DataFrame([row])))
    expected_aas = 15.0 / FAO_WHO_REFERENCE["lysine"]
    assert df.loc[0, "AAS_min"] == pytest.approx(expected_aas)
    assert df.loc[0, "PQS"] == pytest.approx(expected_aas * 0.80)
    assert df.loc[0, "limiting_amino_acid"] == "lysine"
    assert df.loc[0, "is_complete"] == 0


def test_complete_protein_label():
    r = FAO_WHO_REFERENCE
    boost = 1.10
    row = make_row("egg_like", protein=10.0,
                   histidine_mg=r["histidine"]*10*boost,
                   isoleucine_mg=r["isoleucine"]*10*boost,
                   leucine_mg=r["leucine"]*10*boost,
                   lysine_mg=r["lysine"]*10*boost,
                   methionine_mg=r["saa"]*10*boost*0.6,
                   cysteine_mg=r["saa"]*10*boost*0.4,
                   phenylalanine_mg=r["aaa"]*10*boost*0.55,
                   tyrosine_mg=r["aaa"]*10*boost*0.45,
                   threonine_mg=r["threonine"]*10*boost,
                   tryptophan_mg=r["tryptophan"]*10*boost,
                   valine_mg=r["valine"]*10*boost)
    row["category_name"] = "Dairy_Eggs"
    df = compute_all(add_per_gram_protein_features(pd.DataFrame([row])))
    assert df.loc[0, "AAS_min"] == pytest.approx(boost, rel=1e-6)
    assert df.loc[0, "PQS"] == pytest.approx(boost * 0.97, rel=1e-6)
    assert df.loc[0, "is_complete"] == 1


def test_preprocess_drops_low_protein():
    df = pd.DataFrame([
        make_row("water", protein=0.1),
        make_row("chicken", protein=23.0, lysine_mg=2000),
    ])
    cleaned = preprocess(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["food_name"] == "chicken"


def test_preprocess_fills_aa_nans():
    df = pd.DataFrame([make_row("partial", protein=10.0, lysine_mg=500)])
    df.loc[0, "tryptophan_mg"] = None
    cleaned = preprocess(df)
    assert cleaned.loc[0, "tryptophan_mg"] == 0.0


def test_white_rice_is_lysine_limited():
    row = make_row("rice_white", protein=2.69,
                   histidine_mg=59, isoleucine_mg=112, leucine_mg=221,
                   lysine_mg=99, methionine_mg=58, cysteine_mg=28,
                   phenylalanine_mg=141, tyrosine_mg=107,
                   threonine_mg=96, tryptophan_mg=31, valine_mg=159)
    df = compute_all(add_per_gram_protein_features(pd.DataFrame([row])))
    assert df.loc[0, "limiting_amino_acid"] == "lysine"
    assert df.loc[0, "is_complete"] == 0
