import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice

from labels import LABELS

load_dotenv()

DATA_PATH = Path("data/clean.csv")  # gerado pelo data.ipynb (sem avisos nem duplicados)
# Cada corrida grava aqui. Para guardar um resultado, copia a pasta para data/resultados/NN_nome/.
RUN_DIR = Path("data/resultados/ultima_corrida")
OUTPUT_PATH = RUN_DIR / "predictions.csv"
REPORT_PATH = RUN_DIR / "report.txt"
SPLIT_PATH = Path("data/split.csv")  # gerado pelo split.py
INSTRUCTIONS = "Qual é o pedido principal deste email do cliente?"

# Aviso de segurança que aparece em quase todos os emails, às vezes dentro de respostas citadas
# (com ">" e quebras de linha a meio da frase) e com acentos estragados no CSV
# ("N?o", "organiza??o").
_SEP = r"[\s>]+"
_BANNER_1 = (
    r"(?:Este .{1,2} o primeiro e-mail que recebeu deste remetente externo"
    r"|Este e-mail vem de fora da organiza.{1,2}o)\."
)
_BANNER_2 = (
    r"N.{1,2}o clique em links nem abra anexos, a menos que seja um e-mail que esperava receber\."
)
BANNER = re.compile(
    r"[ \t]*" + (_BANNER_1 + " " + _BANNER_2).replace(" ", _SEP) + r"\s*",
    re.IGNORECASE,
)
# Aviso em inglês que alguns remetentes acrescentam ao email.
EXTERNAL = re.compile(
    r"[ \t]*External information\. For external parties or clients\.\s*", re.IGNORECASE
)

# As referências (crab team e LastClassifications) escrevem as categorias de forma diferente
# das chaves de LABELS ("Tarifa Social" vs "Tarifa social", "Emissão 2ª Vias" vs "Emissão de
# 2ª vias", espaços a mais). Comparamos por uma chave sem maiúsculas, espaços nem preposições.
_STOPWORDS = {"de", "da", "das", "do", "dos"}
# "Triagem Manual" não é categoria, fica sem referência.
NOT_A_CATEGORY = {"triagem manual"}


def _key(label: str) -> str:
    return " ".join(w for w in label.lower().split() if w not in _STOPWORDS)


_CANONICAL = {_key(label): label.strip() for label in LABELS}


def clean_body(body: str) -> str:
    body = BANNER.sub("", body)
    body = EXTERNAL.sub("", body)
    return body.strip()


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8", sep=";")
    df["BodyPlainText_masked"] = df["BodyPlainText_masked"].fillna("").map(clean_body)
    return df


def classify(client: TypeSafeClient, subject: str, body: str):
    response = client.system_one(
        state={"subject": subject, "body": clean_body(body)},
        questions={
            "category": Choice(instructions=INSTRUCTIONS, criteria=LABELS),
        },
    )
    return response.choices["category"]


def normalize(label) -> str | None:
    if pd.isna(label):
        return None
    key = _key(label)
    if key in NOT_A_CATEGORY:
        return None
    return _CANONICAL.get(key, label.strip())


def predict(df: pd.DataFrame, workers: int) -> pd.DataFrame:
    with TypeSafeClient() as client:

        def run(row):
            try:
                answer = classify(client, row.Subject_masked, row.BodyPlainText_masked)
                return answer.choice.strip(), answer.confidence, None
            except Exception as e:
                return None, None, repr(e)

        with ThreadPoolExecutor(workers) as pool:
            results = list(pool.map(run, df.itertuples()))

    return pd.DataFrame(
        {
            "IDEvalyze": df["IDEvalyze"].values,
            "subject": df["Subject_masked"].values,
            "ref_crab": df["potencial_classificação_crab_team"].map(normalize).values,
            "ref_last": df["LastClassifications"].map(normalize).values,
            "pred": [r[0] for r in results],
            "confidence": [r[1] for r in results],
            "error": [r[2] for r in results],
        }
    )


def report(preds: pd.DataFrame) -> str:
    lines = []
    errors = preds["error"].notna().sum()
    if errors:
        lines.append(f"{errors} pedidos falharam (ver coluna 'error')\n")

    for ref in ["ref_crab", "ref_last"]:
        scored = preds[preds[ref].notna() & preds["pred"].notna()]
        if scored.empty:
            lines.append(f"== {ref}: sem emails com esta referência\n")
            continue
        correct = scored["pred"] == scored[ref]
        lines.append(f"== {ref}: {correct.mean():.1%} de accuracy ({correct.sum()}/{len(scored)})")

        # Accuracy só nos casos em que o modelo está confiante, e quantos casos isso cobre.
        for t in [0.5, 0.7, 0.9]:
            confident = scored["confidence"] >= t
            if confident.any():
                lines.append(
                    f"   confiança >= {t:.0%}: {correct[confident].mean():.1%} de accuracy"
                    f" em {confident.mean():.0%} dos emails"
                )
        lines.append("")

    scored = preds[preds["ref_crab"].notna() & preds["pred"].notna()]
    lines.append("Confusion matrix (ref_crab nas linhas, previsão nas colunas):")
    lines.append(pd.crosstab(scored["ref_crab"], scored["pred"]).to_string())
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Avalia o Jev no dataset de emails.")
    parser.add_argument("--limit", type=int, help="classificar só N emails (amostra aleatória)")
    parser.add_argument(
        "--only-crab", action="store_true", help="só emails com classificação do crab team"
    )
    parser.add_argument(
        "--split", choices=["dev", "test"], help="só uma parte da divisão em data/split.csv"
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    df = load_dataset()
    output_path, report_path = OUTPUT_PATH, REPORT_PATH
    if args.split:
        split = pd.read_csv(SPLIT_PATH)
        df = df[df["IDEvalyze"].isin(split.loc[split["split"] == args.split, "IDEvalyze"])]
        output_path = OUTPUT_PATH.with_stem(f"{OUTPUT_PATH.stem}_{args.split}")
        report_path = REPORT_PATH.with_stem(f"{REPORT_PATH.stem}_{args.split}")
    if args.only_crab:
        df = df[df["potencial_classificação_crab_team"].notna()]
    if args.limit:
        df = df.sample(min(args.limit, len(df)), random_state=0)

    preds = predict(df, args.workers)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    preds.to_csv(output_path, index=False)
    print(f"Previsões guardadas em {output_path}\n")
    text = report(preds)
    report_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nRelatório guardado em {report_path}")
