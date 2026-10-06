"""Divide o dataset em dev (para afinar as descrições) e test (só para medir no fim).

Correr uma vez: python split.py  ->  gera data/split.csv
"""

from pathlib import Path

import pandas as pd

from classify import load_dataset, normalize

SPLIT_PATH = Path("data/split.csv")
TEST_FRACTION = 0.3

df = load_dataset()

# Estratifica pela referência mais fiável disponível: crab team, senão LastClassifications.
crab = df["potencial_classificação_crab_team"].map(normalize)
last = df["LastClassifications"].map(normalize)
strata = crab.fillna(last).fillna("sem referência")

# Em cada categoria, 30% vão para test. Categorias com 1 só email ficam todas em dev.
test_idx = strata.groupby(strata).sample(frac=TEST_FRACTION, random_state=42).index
split = pd.DataFrame({"IDEvalyze": df["IDEvalyze"], "split": "dev"})
split.loc[test_idx, "split"] = "test"
split.to_csv(SPLIT_PATH, index=False)

print(f"Divisão guardada em {SPLIT_PATH}\n")
summary = pd.crosstab(strata, split["split"], margins=True, margins_name="Total")
print(summary.to_string())
