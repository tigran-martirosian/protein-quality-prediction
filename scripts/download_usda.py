"""Optional: pull amino-acid data from USDA FDC into the CSV format the pipeline reads.

Setup:
    1. Register at https://fdc.nal.usda.gov/api-key-signup.html
    2. set USDA_API_KEY=your_key
    3. python scripts/download_usda.py --out data/raw/foods_usda.csv
"""
import argparse
import csv
import os
import sys
import time
import requests

API_BASE = "https://api.nal.usda.gov/fdc/v1"

NUTRIENT_IDS = {
    "protein_g": 1003, "fat_g": 1004, "carbohydrate_g": 1005, "energy_kcal": 1008,
    "tryptophan_mg": 1210, "threonine_mg": 1211, "isoleucine_mg": 1212,
    "leucine_mg": 1213, "lysine_mg": 1214, "methionine_mg": 1215,
    "cysteine_mg": 1216, "phenylalanine_mg": 1217, "tyrosine_mg": 1218,
    "valine_mg": 1219, "histidine_mg": 1221,
}

QUERIES = {
    "Meat":       ["chicken breast", "beef ground", "pork loin", "turkey breast", "lamb"],
    "Seafood":    ["salmon atlantic", "tuna yellowfin", "cod atlantic", "shrimp", "tilapia"],
    "Dairy_Eggs": ["egg whole raw", "milk whole", "greek yogurt", "cheddar cheese"],
    "Legumes":    ["lentils cooked", "black beans cooked", "chickpeas cooked",
                   "soybeans cooked", "tofu firm"],
    "Grains":     ["rice white cooked", "rice brown cooked", "quinoa cooked",
                   "oats rolled", "wheat flour whole"],
    "Nuts_Seeds": ["almonds raw", "walnuts english", "pumpkin seeds", "sesame seeds"],
    "Vegetables": ["broccoli raw", "spinach raw", "kale raw", "potato raw"],
}
ANIMAL_CATS = {"Meat", "Seafood", "Dairy_Eggs"}


def search(query, key, n=2):
    r = requests.get(f"{API_BASE}/foods/search",
                     params={"api_key": key, "query": query,
                             "dataType": ["Foundation", "SR Legacy"], "pageSize": n},
                     timeout=30)
    r.raise_for_status()
    return r.json().get("foods", [])[:n]


def fetch(fdc_id, key):
    r = requests.get(f"{API_BASE}/food/{fdc_id}", params={"api_key": key}, timeout=30)
    r.raise_for_status()
    return r.json()


def extract(detail, category):
    nmap = {}
    for fn in detail.get("foodNutrients", []):
        nid = fn.get("nutrient", {}).get("id")
        amount = fn.get("amount")
        if nid is not None and amount is not None:
            nmap[nid] = amount
    row = {
        "food_name": detail.get("description", "").strip(),
        "category_name": category,
        "is_animal": 1 if category in ANIMAL_CATS else 0,
        "fdc_id": detail.get("fdcId"),
    }
    for col, nid in NUTRIENT_IDS.items():
        row[col] = nmap.get(nid, "")
    return row if row["protein_g"] else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/foods_usda.csv")
    ap.add_argument("--per-query", type=int, default=2)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    key = os.environ.get("USDA_API_KEY")
    if not key:
        print("set USDA_API_KEY", file=sys.stderr); return 1

    rows = []
    for cat, queries in QUERIES.items():
        for q in queries:
            print(f"[{cat}] {q}")
            for hit in search(q, key, args.per_query):
                fdc_id = hit.get("fdcId")
                if not fdc_id:
                    continue
                time.sleep(args.sleep)
                row = extract(fetch(fdc_id, key), cat)
                if row:
                    rows.append(row)
            time.sleep(args.sleep)

    header = ["food_name", "category_name", "is_animal", "fdc_id"] + list(NUTRIENT_IDS.keys())
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows: w.writerow(r)

    print(f"wrote {len(rows)} foods to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
