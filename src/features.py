"""Compute mg of each essential amino acid per gram of total protein."""


def add_per_gram_protein_features(df):
    df = df.copy()
    p = df["protein_g"]
    df["histidine_per_g"]  = df["histidine_mg"]  / p
    df["isoleucine_per_g"] = df["isoleucine_mg"] / p
    df["leucine_per_g"]    = df["leucine_mg"]    / p
    df["lysine_per_g"]     = df["lysine_mg"]     / p
    df["saa_per_g"] = (df["methionine_mg"]    + df["cysteine_mg"]) / p
    df["aaa_per_g"] = (df["phenylalanine_mg"] + df["tyrosine_mg"]) / p
    df["threonine_per_g"]  = df["threonine_mg"]  / p
    df["tryptophan_per_g"] = df["tryptophan_mg"] / p
    df["valine_per_g"]     = df["valine_mg"]     / p
    return df
