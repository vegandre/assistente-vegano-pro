import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🌱 Teste de Conexão Vegana")

# Link direto sem NENHUM caractere extra
link = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Tentativa de leitura simples
    df = conn.read(spreadsheet=link, worksheet="LISTA ALIMENTOS", header=7)
    st.success("Conectado com sucesso!")
    st.dataframe(df.head())
except Exception as e:
    st.error(f"Erro: {e}")
