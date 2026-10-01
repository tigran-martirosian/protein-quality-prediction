"""Build the SQL schema and load the food data into it."""
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from .config import SQL_SCHEMA, DEFAULT_SQLITE_PATH


def make_engine(backend="sqlite", sqlite_path=DEFAULT_SQLITE_PATH, pg_url=None):
    if backend == "postgres":
        url = pg_url or os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("set DATABASE_URL for postgres backend")
        return create_engine(url, future=True)
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{sqlite_path}", future=True)


def create_schema(engine, schema_path=SQL_SCHEMA):
    sql = Path(schema_path).read_text()
    cleaned = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    statements = [s.strip() for s in cleaned.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))


def populate(engine, df):
    categories = (
        df[["category_name", "is_animal"]]
        .drop_duplicates()
        .sort_values("category_name")
        .reset_index(drop=True)
    )
    categories.insert(0, "category_id", categories.index + 1)
    cat_map = dict(zip(categories["category_name"], categories["category_id"]))

    foods = pd.DataFrame({
        "food_id":     df["food_id"],
        "food_name":   df["food_name"],
        "category_id": df["category_name"].map(cat_map),
        "fdc_id":      df.get("fdc_id"),
    })

    macros = df[["food_id", "protein_g", "fat_g", "carbohydrate_g", "energy_kcal"]].copy()

    aa_cols = [
        "food_id", "histidine_mg", "isoleucine_mg", "leucine_mg", "lysine_mg",
        "methionine_mg", "cysteine_mg", "phenylalanine_mg", "tyrosine_mg",
        "threonine_mg", "tryptophan_mg", "valine_mg",
    ]
    aminos = df[aa_cols].copy()

    with engine.begin() as conn:
        categories.to_sql("food_categories", conn, if_exists="append", index=False)
        foods.to_sql("foods", conn, if_exists="append", index=False)
        macros.to_sql("macronutrients", conn, if_exists="append", index=False)
        aminos.to_sql("amino_acids", conn, if_exists="append", index=False)


def load_feature_view(engine):
    return pd.read_sql("SELECT * FROM food_features", engine)
