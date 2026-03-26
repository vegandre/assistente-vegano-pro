import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração básica da página
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")

# Título do App
st.title("🌱 Assistente Nutricional Vegano")

# URL da sua planilha (ajuste se necessário)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"

try:
    # Conexão com o Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=URL_PLANILHA, worksheet="LISTA ALIMENTOS", header=7)
    
    # Exibir os dados básicos para teste
    st.write("### Lista de Alimentos Carregada!")
    st.dataframe(df.head()) # Mostra as primeiras 5 linhas

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Verifique se a planilha está compartilhada como 'Qualquer pessoa com o link'!")
