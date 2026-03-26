import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")

st.title("🌱 Assistente Nutricional Vegano")

# URL corrigida (removidos espaços e caracteres invisíveis)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"
URL_PLANILHA = URL_PLANILHA.strip()

try:
    # Conexão simplificada
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentativa de leitura da aba específica
    df = conn.read(spreadsheet=URL_PLANILHA, worksheet="LISTA ALIMENTOS", header=7)
    
    st.success("✅ Dados carregados com sucesso!")
    st.write("### Prévia da Lista de Alimentos:")
    st.dataframe(df.head(10)) # Mostra as 10 primeiras linhas para teste

except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.info("Dica: Verifique se o nome da aba na planilha é exatamente 'LISTA ALIMENTOS' (com letras maiúsculas).")
