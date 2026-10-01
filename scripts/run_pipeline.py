"""End-to-end pipeline: load -> preprocess -> DB -> features -> score -> model -> plot."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import config
from src.data_loader import load_foods
from src.preprocess  import preprocess
from src.db_setup    import make_engine, create_schema, populate, load_feature_view
from src.features    import add_per_gram_protein_features
from src.scoring     import compute_all
from src.model       import train_and_evaluate, format_result, classification_text_report
from src.visualize   import make_all_plots


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=None, help="CSV path (default: sample)")
    ap.add_argument("--db", choices=("sqlite", "postgres"), default="sqlite")
    ap.add_argument("--skip-plots", action="store_true")
    return ap.parse_args()


def main():
    args = parse_args()
    for d in (config.REPORTS_DIR, config.FIGURES_DIR):
        d.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    df = load_foods(args.input)
    print(f"  {len(df)} rows, categories: {sorted(df['category_name'].unique())}")

    print("Preprocessing...")
    df = preprocess(df)
    print(f"  {len(df)} rows after cleaning")

    print(f"Building database ({args.db})...")
    engine = make_engine(backend=args.db)
    create_schema(engine)
    populate(engine, df)

    df = load_feature_view(engine)
    df = add_per_gram_protein_features(df)
    df = compute_all(df)

    n_complete = int(df["is_complete"].sum())
    print(f"Scoring complete. {n_complete} / {len(df)} foods are complete proteins.")
    print("Top 5:")
    for _, r in df.nlargest(5, "PQS")[["food_name", "PQS", "limiting_amino_acid"]].iterrows():
        print(f"  {r['food_name']:30s}  PQS={r['PQS']:.3f}  (limited by {r['limiting_amino_acid']})")

    cols = ["food_name", "category_name", "protein_g", "PQS", "limiting_amino_acid", "is_complete"]
    ranking = df[cols].sort_values("PQS", ascending=False).reset_index(drop=True)
    ranking_path = config.REPORTS_DIR / "protein_ranking.csv"
    ranking.to_csv(ranking_path, index=False)
    print(f"Saved ranking to {ranking_path}")

    print("Training models...")
    results = train_and_evaluate(df)
    metrics_path = config.REPORTS_DIR / "model_metrics.txt"
    with open(metrics_path, "w") as fh:
        for r in results:
            text = format_result(r)
            print(text); print()
            fh.write(text + "\n\n")
        fh.write("Random Forest classification_report:\n")
        fh.write(classification_text_report(df) + "\n")
    print(f"Saved metrics to {metrics_path}")

    if not args.skip_plots:
        print("Generating plots...")
        for p in make_all_plots(df):
            if p:
                print(f"  {p}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
