import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Teste de Conexão Vegana")

# 1. Usando apenas o ID da planilha (mais seguro contra erros de colagem)
ID_PLANILHA = "1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr"
URL_LIMPA = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/edit#gid=1577491175"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Tentando ler removendo qualquer espaço extra no nome da aba
    df = conn.read(
        spreadsheet=URL_LIMPA, 
        worksheet="LISTA ALIMENTOS", 
        header=7
    )
    
    st.success("✅ Finalmente conectamos!")
    st.dataframe(df.head())

except Exception as e:
    # Exibe o erro de forma mais detalhada para investigarmos
    st.error(f"Erro detectado: {e}")
    st.info("Dica: Se o erro persistir, verifique se a aba no Google Sheets se chama exatamente 'LISTA ALIMENTOS' sem espaços no final.")
