"""Plots saved to results/figures/."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import ESSENTIAL_AA_FEATURES, FIGURES_DIR

sns.set_theme(style="whitegrid", context="talk", palette="deep")

AA_DISPLAY = {
    "histidine": "Histidine", "isoleucine": "Isoleucine", "leucine": "Leucine",
    "lysine": "Lysine", "saa": "Methionine + Cysteine", "aaa": "Phenylalanine + Tyrosine",
    "threonine": "Threonine", "tryptophan": "Tryptophan", "valine": "Valine",
}


def pretty_category(name):
    return name.replace("_", " & ")


def pretty_aa(name):
    base = name.replace("_per_g", "").lower()
    return AA_DISPLAY.get(base, base.title())


def plot_top_ranking(df, top_n=20, out_dir=FIGURES_DIR):
    top = df.nlargest(top_n, "PQS").iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 0.35 * top_n + 1.5))
    colors = ["#2ca02c" if c else "#1f77b4" for c in top["is_complete"]]
    ax.barh(top["food_name"], top["PQS"], color=colors)
    ax.axvline(1.0, color="red", linestyle="--", linewidth=1.2,
               label="Complete-protein threshold (PQS = 1.0)")
    ax.set_xlabel("Protein Quality Score")
    ax.set_title(f"Top {top_n} Foods by Protein Quality")
    ax.legend(loc="lower right")
    plt.tight_layout()
    path = out_dir / "protein_quality_ranking.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_limiting_amino_acids(df, out_dir=FIGURES_DIR):
    counts = df["limiting_amino_acid"].map(pretty_aa).value_counts()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=counts.index, y=counts.values, ax=ax, color="#ff7f0e")
    ax.set_xlabel("Limiting Amino Acid")
    ax.set_ylabel("Number of Foods")
    ax.set_title("Most Common Limiting Amino Acids")
    plt.xticks(rotation=30)
    plt.tight_layout()
    path = out_dir / "limiting_amino_acids.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_category_pqs_boxplot(df, out_dir=FIGURES_DIR):
    df = df.copy()
    df["category_name"] = df["category_name"].map(pretty_category)
    order = (df.groupby("category_name")["PQS"].median()
               .sort_values(ascending=False).index.tolist())
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x="category_name", y="PQS", order=order, ax=ax)
    sns.stripplot(data=df, x="category_name", y="PQS", order=order,
                  color="black", size=3, alpha=0.5, ax=ax)
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.2)
    ax.set_xlabel("Food Category")
    ax.set_ylabel("Protein Quality Score")
    ax.set_title("Protein Quality Distribution by Food Category")
    plt.xticks(rotation=30)
    plt.tight_layout()
    path = out_dir / "category_pqs_boxplot.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_amino_acid_heatmap(df, top_n=25, out_dir=FIGURES_DIR):
    subset = df.nlargest(top_n, "PQS").set_index("food_name")[ESSENTIAL_AA_FEATURES]
    subset.columns = [pretty_aa(c) for c in subset.columns]
    fig, ax = plt.subplots(figsize=(11, 0.35 * top_n + 2))
    sns.heatmap(subset, cmap="viridis", ax=ax,
                cbar_kws={"label": "mg AA / g protein"}, linewidths=0.4)
    ax.set_title(f"Essential Amino Acid Density of Top {top_n} Foods")
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.tight_layout()
    path = out_dir / "aa_heatmap.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_clusters_pca(df, k=4, out_dir=FIGURES_DIR):
    X = df[ESSENTIAL_AA_FEATURES].values
    Xs = StandardScaler().fit_transform(X)
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(Xs)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(Xs)

    fig, ax = plt.subplots(figsize=(10, 7))
    palette = sns.color_palette("tab10", k)
    for c in range(k):
        m = labels == c
        ax.scatter(coords[m, 0], coords[m, 1], s=80, alpha=0.75,
                   color=palette[c], label=f"Cluster {c}")

    tmp = df.copy()
    tmp["_c"] = labels; tmp["_x"] = coords[:, 0]; tmp["_y"] = coords[:, 1]
    for _, row in tmp.sort_values("PQS", ascending=False).groupby("_c").head(2).iterrows():
        ax.text(row["_x"] + 0.05, row["_y"] + 0.05, row["food_name"], fontsize=8, alpha=0.8)

    var = pca.explained_variance_ratio_
    ax.set_xlabel(f"PC1 ({var[0]:.0%} variance)")
    ax.set_ylabel(f"PC2 ({var[1]:.0%} variance)")
    ax.set_title(f"K-means (k={k}) on Amino Acid Density")
    ax.legend()
    plt.tight_layout()
    path = out_dir / "cluster_pca.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_logreg_coefficients(df, out_dir=FIGURES_DIR):
    X = df[ESSENTIAL_AA_FEATURES].values
    y = df["is_complete"].astype(int).values
    if len(np.unique(y)) < 2:
        return None
    pipe = Pipeline([("scale", StandardScaler()),
                     ("clf",   LogisticRegression(max_iter=1000, random_state=42))])
    pipe.fit(X, y)
    coefs = pipe.named_steps["clf"].coef_[0]
    order = np.argsort(coefs)
    names = [pretty_aa(ESSENTIAL_AA_FEATURES[i]) for i in order]
    vals = coefs[order]

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = ["#d62728" if v < 0 else "#2ca02c" for v in vals]
    ax.barh(names, vals, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Standardized Coefficient")
    ax.set_title("Logistic Regression Predictors of Complete Protein")
    plt.tight_layout()
    path = out_dir / "logreg_coefficients.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def make_all_plots(df, out_dir=FIGURES_DIR):
    return [
        plot_top_ranking(df, out_dir=out_dir),
        plot_limiting_amino_acids(df, out_dir=out_dir),
        plot_category_pqs_boxplot(df, out_dir=out_dir),
        plot_amino_acid_heatmap(df, out_dir=out_dir),
        plot_clusters_pca(df, out_dir=out_dir),
        plot_logreg_coefficients(df, out_dir=out_dir),
    ]
