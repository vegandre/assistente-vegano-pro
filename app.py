import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Assistente Nutricional Vegano")

# Link direto e limpo
URL = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"

try:
    # Cria a conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lê os dados - especificando a aba e onde começam os títulos
    df = conn.read(spreadsheet=URL, worksheet="LISTA ALIMENTOS", header=7)
    
    if df is not None:
        st.success("✅ Conexão estabelecida!")
        st.write("### Dados da Planilha:")
        st.dataframe(df.head(10))
except Exception as e:
    st.error(f"Erro técnico: {e}")
    st.warning("Verifique se a planilha está aberta para 'Qualquer pessoa com o link' no Google Sheets.")
