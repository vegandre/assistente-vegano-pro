import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Teste de Conexão Vegana")

# 1. URL Principal (Removi o gid do final para evitar o erro 404)
URL_PRINCIPAL = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit"

try:
    # 2. Estabelecer conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 3. Ler a aba 'dados'
    # Importante: O nome deve ser exatamente como está no seu print: dados
    df = conn.read(spreadsheet=URL_PRINCIPAL, worksheet="dados", header=7)
    
    if df is not None:
        st.success("✅ CONECTADO! A tabela foi encontrada.")
        st.subheader("Visualizando os dados da aba 'dados':")
        st.dataframe(df.head(10))

except Exception as e:
    st.error(f"Erro ao acessar a aba: {e}")
    st.info("Dica: Se aparecer erro de 'Worksheet not found', verifique se não há um espaço acidental em 'dados ' na planilha.")
