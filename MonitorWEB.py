import streamlit as st
import pandas as pd
import requests
from io import StringIO

# =========================
# CONFIGURAÇÕES
# =========================

GITHUB_OWNER = "monitorgolive"
GITHUB_REPO = "monitor"
BRANCH = "main"

PASTA_GRUPO = "grupo"
PASTA_DADOS = "dados"

BASE_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"

st.set_page_config(
    page_title="Monitor",
    layout="wide"
)

# =========================
# FUNÇÕES
# =========================

@st.cache_data(show_spinner=False)
def listar_arquivos(pasta):
    url = f"{BASE_API_URL}/{pasta}?ref={BRANCH}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


@st.cache_data(show_spinner=False)
def ler_csv_github(pasta, nome):
    url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{BRANCH}/{pasta}/{nome}.csv"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text))


# =========================
# SIDEBAR
# =========================

st.sidebar.header("Filtros")

# --- Seleção do Grupo ---
grupos = sorted(
    arq["name"].replace(".csv", "")
    for arq in listar_arquivos(PASTA_GRUPO)
    if arq["name"].endswith(".csv")
)

grupo = st.sidebar.selectbox("Grupo", ["Selecione..."] + grupos)

if grupo == "Selecione...":
    st.info("Selecione um grupo para iniciar.")
    st.stop()

# =========================
# LEITURA DO ARQUIVO DADOS
# =========================

st.title(grupo)

try:
    df_dados = ler_csv_github(PASTA_DADOS, grupo)
except Exception:
    st.error("Arquivo correspondente não encontrado na pasta dados.")
    st.stop()

# =========================
# FILTRO PELA PRIMEIRA COLUNA
# =========================

coluna_chave = df_dados.columns[0]

valores = sorted(
    df_dados[coluna_chave]
    .dropna()
    .astype(str)
    .unique()
)

selecionados = st.sidebar.multiselect(
    f"Selecione {coluna_chave}",
    valores
)

if not selecionados:
    st.info(f"Selecione ao menos uma Revenda para exibir os dados.")
    st.stop()

df_filtrado = df_dados[
    df_dados[coluna_chave].astype(str).isin(selecionados)
]

# =========================
# EXIBIÇÃO
# =========================

st.caption(f"Registros exibidos: {len(df_filtrado)}")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)
