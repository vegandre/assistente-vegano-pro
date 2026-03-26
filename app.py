import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Teste de Conexão Vegana")

# Link direto e ID isolado para evitar erros de caractere
ID = "1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr"
URL = f"https://docs.google.com/spreadsheets/d/{ID}/edit#gid=1577491175"

try:
    # Criando a conexão do zero
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lendo a aba que acabamos de renomear para 'dados'
    # O .strip() garante que não escape nenhum espaço
    df = conn.read(spreadsheet=URL.strip(), worksheet="dados", header=7)
    
    st.success("✅ Conectado com sucesso!")
    st.dataframe(df.head(10))

except Exception as e:
    st.error(f"Erro técnico: {e}")
    st.info("Se o erro de 'control characters' persistir, limpe os SECRETS no painel do Streamlit.")
