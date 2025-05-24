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

st.set_page_config(
    page_title="My Budget Dashboard",
    layout="wide"
)

st.title("💰 My Budget Dashboard")

@st.cache_data
def load_csvs(pattern):
    """Carrega todos os CSVs que batem com o padrão e concatena num único DataFrame,
       ignorando arquivos vazios ou sem colunas."""
    files = glob.glob(os.path.join(DATA_DIR, pattern))
    dfs = []
    for f in files:
        # pula arquivos de tamanho zero
        if os.path.getsize(f) == 0:
            st.warning(f"Arquivo vazio: {os.path.basename(f)} — pulando.")
            continue

        try:
            df = pd.read_csv(f, parse_dates=["data"], dayfirst=True)
        except pd.errors.EmptyDataError:
            st.warning(f"Sem colunas em: {os.path.basename(f)} — pulando.")
            continue

        # se acabou sem colunas, pula
        if df.empty:
            st.warning(f"Dados nulos em: {os.path.basename(f)} — pulando.")
            continue

        df["origem"] = os.path.basename(f).replace(".csv", "")
        dfs.append(df)

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()
        return pd.DataFrame()

# 1) Extratos bancários e cartões
extratos = load_csvs("extratos_*.csv")
cartoes  = load_csvs("cartao_*.csv")
invest   = load_csvs("investimentos*.csv")
emprest  = load_csvs("emprestimos*.csv")

# Preprocessamento básico
def preprocess(df):
    if df.empty: 
        return df
    df = df.rename(columns=lambda c: c.strip().lower())
    # garante colunas mínimas: data, descrição, valor
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    return df

extratos = preprocess(extratos)
cartoes  = preprocess(cartoes)
invest   = preprocess(invest)
emprest  = preprocess(emprest)

# Sidebar: filtro de data
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data inicial", value=extratos["data"].min())
end_date   = st.sidebar.date_input("Data final",   value=extratos["data"].max())
mask = (extratos["data"] >= pd.to_datetime(start_date)) & (extratos["data"] <= pd.to_datetime(end_date))

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
total_saldo = extratos.loc[mask, "valor"].sum() + invest["valor"].sum() - emprest["valor"].sum()
col1.metric("Saldo Atual (Conta)", f"R$ {extratos.loc[mask, 'valor'].sum():,.2f}")
col2.metric("Investimentos",      f"R$ {invest['valor'].sum():,.2f}")
col3.metric("Empréstimos",         f"R$ {emprest['valor'].sum():,.2f}")
col4.metric("Total Líquido",       f"R$ {total_saldo:,.2f}")

st.markdown("---")

# Série temporal de despesas e receitas
st.subheader("Fluxo ao longo do tempo")
ts = extratos.loc[mask].groupby(pd.Grouper(key="data", freq="M"))["valor"].sum().reset_index()
fig_ts = px.line(ts, x="data", y="valor", title="Receitas/Despesas Mensais")
st.plotly_chart(fig_ts, use_container_width=True)

# Gráfico por categoria (se existir coluna categoria)
if "categoria" in extratos.columns:
    st.subheader("Gastos por Categoria")
    cat = (extratos.loc[mask]
           .groupby("categoria")["valor"]
           .sum()
           .reset_index()
           .sort_values("valor", ascending=False))
    fig_cat = px.bar(cat, x="categoria", y="valor", title="Despesa por Categoria")
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# Tabelas detalhadas
st.subheader("Detalhamento dos Registros")
tab = st.tabs(["Conta Corrente", "Cartão de Crédito", "Investimentos", "Empréstimos"])
with tab[0]:
    st.dataframe(extratos.loc[mask].sort_values("data", ascending=False), use_container_width=True)
with tab[1]:
    st.dataframe(cartoes.sort_values("data", ascending=False), use_container_width=True)
with tab[2]:
    st.dataframe(invest.sort_values("data", ascending=False), use_container_width=True)
with tab[3]:
    st.dataframe(emprest.sort_values("data", ascending=False), use_container_width=True)

# === Insights via OpenAI ===
if OPENAI_API_KEY:
    st.markdown("---")
    st.subheader("🤖 Insights Automáticos")
    if st.button("Gerar insight geral"):
        with st.spinner("Analisando dados..."):
            prompt = (
                f"Tenho os seguintes dados de finanças pessoais até {end_date}:\n"
                f"- Total em conta: R$ {extratos.loc[mask,'valor'].sum():,.2f}\n"
                f"- Total investimento: R$ {invest['valor'].sum():,.2f}\n"
                f"- Total empréstimos: R$ {emprest['valor'].sum():,.2f}\n"
                "Gere um breve resumo de insights e recomendações."
            )
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content": prompt}]
            )
            st.write(resp.choices[0].message.content)
