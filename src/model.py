"""Train Logistic Regression and Random Forest classifiers on AA features."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import ESSENTIAL_AA_FEATURES


def evaluate_model(name, pipeline, X, y, seed=42):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    cv_acc = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
    cv_f1  = cross_val_score(pipeline, X, y, cv=cv, scoring="f1")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=seed)
    pipeline.fit(X_tr, y_tr)
    y_pred = pipeline.predict(X_te)

    final = pipeline.steps[-1][1]
    if hasattr(final, "feature_importances_"):
        importance = dict(zip(X.columns, final.feature_importances_))
    elif hasattr(final, "coef_"):
        importance = dict(zip(X.columns, final.coef_[0]))
    else:
        importance = {}

    return {
        "name": name,
        "cv_accuracy_mean": float(np.mean(cv_acc)),
        "cv_accuracy_std":  float(np.std(cv_acc)),
        "cv_f1_mean":       float(np.mean(cv_f1)),
        "test_accuracy":    float(accuracy_score(y_te, y_pred)),
        "test_precision":   float(precision_score(y_te, y_pred, zero_division=0)),
        "test_recall":      float(recall_score(y_te, y_pred, zero_division=0)),
        "test_f1":          float(f1_score(y_te, y_pred, zero_division=0)),
        "confusion":        confusion_matrix(y_te, y_pred).tolist(),
        "feature_importance": importance,
    }


def format_result(r):
    lines = [
        f"Model: {r['name']}",
        f"  CV accuracy : {r['cv_accuracy_mean']:.3f} +/- {r['cv_accuracy_std']:.3f}",
        f"  CV F1       : {r['cv_f1_mean']:.3f}",
        f"  Test acc    : {r['test_accuracy']:.3f}",
        f"  Test prec.  : {r['test_precision']:.3f}",
        f"  Test recall : {r['test_recall']:.3f}",
        f"  Test F1     : {r['test_f1']:.3f}",
        f"  Confusion   : {r['confusion']}",
    ]
    if r["feature_importance"]:
        lines.append("  Top features:")
        top = sorted(r["feature_importance"].items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]
        for name, val in top:
            lines.append(f"    {name:24s} {val:+.3f}")
    return "\n".join(lines)


def train_and_evaluate(df):
    X = df[ESSENTIAL_AA_FEATURES].copy()
    y = df["is_complete"].astype(int)
    if y.nunique() < 2:
        print(f"only one class present ({y.unique()}); skipping")
        return []

    lr = Pipeline([
        ("scale", StandardScaler()),
        ("clf",   LogisticRegression(max_iter=1000, random_state=42)),
    ])
    rf = Pipeline([
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1)),
    ])
    return [evaluate_model("Logistic Regression", lr, X, y),
            evaluate_model("Random Forest", rf, X, y)]


def classification_text_report(df):
    X = df[ESSENTIAL_AA_FEATURES]
    y = df["is_complete"].astype(int)
    if y.nunique() < 2:
        return "only one class present"
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1)
    rf.fit(X_tr, y_tr)
    return classification_report(y_te, rf.predict(X_te), zero_division=0)
