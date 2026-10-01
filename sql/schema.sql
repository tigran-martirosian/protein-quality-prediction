DROP TABLE IF EXISTS amino_acids;
DROP TABLE IF EXISTS macronutrients;
DROP TABLE IF EXISTS foods;
DROP TABLE IF EXISTS food_categories;

CREATE TABLE food_categories (
    category_id   INTEGER PRIMARY KEY,
    category_name VARCHAR(64) NOT NULL UNIQUE,
    is_animal     INTEGER NOT NULL
);

CREATE TABLE foods (
    food_id     INTEGER PRIMARY KEY,
    food_name   VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL,
    fdc_id      INTEGER,
    FOREIGN KEY (category_id) REFERENCES food_categories(category_id)
);

CREATE INDEX idx_foods_category ON foods(category_id);

CREATE TABLE macronutrients (
    food_id        INTEGER PRIMARY KEY,
    protein_g      REAL NOT NULL,
    fat_g          REAL,
    carbohydrate_g REAL,
    energy_kcal    REAL,
    FOREIGN KEY (food_id) REFERENCES foods(food_id)
);

CREATE TABLE amino_acids (
    food_id          INTEGER PRIMARY KEY,
    histidine_mg     REAL,
    isoleucine_mg    REAL,
    leucine_mg       REAL,
    lysine_mg        REAL,
    methionine_mg    REAL,
    cysteine_mg      REAL,
    phenylalanine_mg REAL,
    tyrosine_mg      REAL,
    threonine_mg     REAL,
    tryptophan_mg    REAL,
    valine_mg        REAL,
    FOREIGN KEY (food_id) REFERENCES foods(food_id)
);

DROP VIEW IF EXISTS food_features;
CREATE VIEW food_features AS
SELECT
    f.food_id, f.food_name, c.category_name, c.is_animal,
    m.protein_g, m.fat_g, m.carbohydrate_g, m.energy_kcal,
    a.histidine_mg, a.isoleucine_mg, a.leucine_mg, a.lysine_mg,
    a.methionine_mg, a.cysteine_mg, a.phenylalanine_mg, a.tyrosine_mg,
    a.threonine_mg, a.tryptophan_mg, a.valine_mg
FROM foods f
JOIN food_categories c ON f.category_id = c.category_id
JOIN macronutrients m  ON f.food_id = m.food_id
JOIN amino_acids a     ON f.food_id = a.food_id;
