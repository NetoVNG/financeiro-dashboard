import os
import glob
import pandas as pd
import plotly.express as px
import streamlit as st
import openai

# === Configurações ===
DATA_DIR = "data"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="My Budget Dashboard", layout="wide")
st.title("💰 My Budget Dashboard")

@st.cache_data
def load_csvs(pattern):
    """Carrega e concatena CSVs, ignorando arquivos vazios ou mal formatados."""
    files = glob.glob(os.path.join(DATA_DIR, pattern))
    dfs = []
    for f in files:
        if os.path.getsize(f) == 0:
            st.warning(f"Arquivo vazio: {os.path.basename(f)} — pulando.")
            continue
        try:
            df = pd.read_csv(f, parse_dates=["data"], dayfirst=True)
        except pd.errors.EmptyDataError:
            st.warning(f"Sem colunas em: {os.path.basename(f)} — pulando.")
            continue
        if df.empty:
            st.warning(f"Dados nulos em: {os.path.basename(f)} — pulando.")
            continue
        df["origem"] = os.path.basename(f).replace(".csv", "")
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

@st.cache_data
def preprocess(df):
    df = df.rename(columns=lambda c: c.strip().lower())
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    return df

# === Carrega apenas extratos ===
extratos = load_csvs("extratos_*.csv")
extratos = preprocess(extratos)
if extratos.empty or "data" not in extratos.columns:
    st.warning(
        "😕 Não há dados de extratos carregados. "
        "Coloque arquivos em 'data/' com colunas: data, descrição, valor."
    )
    st.stop()

# === Sidebar de filtros ===
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data inicial", value=extratos["data"].min().date())
end_date = st.sidebar.date_input("Data final", value=extratos["data"].max().date())
mask = (
    (extratos["data"] >= pd.to_datetime(start_date)) &
    (extratos["data"] <= pd.to_datetime(end_date))
)

# === KPI Cards ===
col1, col2 = st.columns(2)
total_saldo = extratos.loc[mask, "valor"].sum()
col1.metric("Saldo Atual (Conta)", f"R$ {total_saldo:,.2f}")
col2.metric("Registros", f"{len(extratos.loc[mask]):d}")

st.markdown("---")

# === Série Temporal ===
st.subheader("Fluxo ao longo do tempo")
ts = (
    extratos.loc[mask]
    .groupby(pd.Grouper(key="data", freq="M"))["valor"]
    .sum()
    .reset_index()
)
fig_ts = px.line(ts, x="data", y="valor", title="Receitas/Despesas Mensais")
st.plotly_chart(fig_ts, use_container_width=True)

# === Gráfico por Categoria ===
if "categoria" in extratos.columns:
    st.subheader("Gastos por Categoria")
    cat = (
        extratos.loc[mask]
        .groupby("categoria")["valor"]
        .sum()
        .reset_index()
        .sort_values("valor", ascending=False)
    )
    fig_cat = px.bar(cat, x="categoria", y="valor", title="Despesa por Categoria")
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# === Tabela de Detalhes ===
st.subheader("Detalhamento dos Registros")
st.dataframe(
    extratos.loc[mask].sort_values("data", ascending=False),
    use_container_width=True
)

# === Insights opcionais ===
if OPENAI_API_KEY:
    st.markdown("---")
    st.subheader("🤖 Insights Automáticos")
    if st.button("Gerar insight geral"):
        with st.spinner("Analisando dados..."):
            prompt = (
                f"Tenho os seguintes dados financeiros até {end_date}:\n"
                f"- Total em conta: R$ {total_saldo:,.2f}\n"
                "Gere um breve resumo de insights e recomendações."
            )
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content": prompt}]
            )
            st.write(resp.choices[0].message.content)