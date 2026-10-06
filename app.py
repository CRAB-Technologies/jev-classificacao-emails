import pandas as pd
import streamlit as st
from typesafe_sdk import TypeSafeClient

import classify as jev


@st.cache_resource
def get_client() -> TypeSafeClient:
    return TypeSafeClient()


@st.cache_data
def load_examples() -> pd.DataFrame | None:
    if not jev.DATA_PATH.exists():
        return None
    return jev.load_dataset()


def load_random_example():
    row = load_examples().sample(1).iloc[0]
    st.session_state.subject = row["Subject_masked"]
    st.session_state.body = row["BodyPlainText_masked"]
    st.session_state.reference = {
        "LastClassifications": row["LastClassifications"],
        "crab_team": row["potencial_classificação_crab_team"],
    }


st.set_page_config(page_title="Jev · Classificação de emails", layout="wide")
st.title("Classificação de emails com Jev")

left, right = st.columns(2, gap="large")

with left:
    if load_examples() is not None:
        st.button("Carregar exemplo aleatório do dataset", on_click=load_random_example)

    subject = st.text_input("Assunto", key="subject")
    body = st.text_area("Corpo do email", key="body", height=300)

    if ref := st.session_state.get("reference"):
        crab = ref["crab_team"] if pd.notna(ref["crab_team"]) else "—"
        st.caption(
            f"Referência · LastClassifications: **{ref['LastClassifications']}**"
            f" · crab team: **{crab}**"
        )

    classify_clicked = st.button("Classificar", type="primary", disabled=not body.strip())

    if classify_clicked:
        with st.expander("Texto enviado ao modelo (após limpeza)"):
            st.text(jev.clean_body(body))

with right:
    if classify_clicked:
        with st.spinner("A classificar..."):
            answer = jev.classify(get_client(), subject, body)

        col1, col2 = st.columns(2)
        col1.metric("Categoria", answer.choice.strip())
        col2.metric("Confiança", f"{answer.confidence:.0%}")

        probs = (
            pd.DataFrame(
                {
                    "Categoria": [k.strip() for k in answer.probabilities],
                    "Probabilidade": list(answer.probabilities.values()),
                }
            )
            .sort_values("Probabilidade", ascending=False)
            .reset_index(drop=True)
        )
        st.dataframe(
            probs,
            hide_index=True,
            width="stretch",
            height=35 * (len(probs) + 1) + 3,
            column_config={
                "Probabilidade": st.column_config.ProgressColumn(
                    format="percent", min_value=0.0, max_value=1.0
                ),
            },
        )
    else:
        st.info("O resultado da classificação aparece aqui.")
