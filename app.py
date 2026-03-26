import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")

st.title("🌱 Assistente Nutricional Vegano")

# 1. Definindo a URL de forma ultra-limpa
# Certifique-se de que não há espaços antes ou depois das aspas
url_base = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"

# 2. Limpeza profunda de caracteres invisíveis
url_final = "".join(url_base.split()) 

try:
    # 3. Estabelecendo a conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 4. Leitura dos dados
    # header=7 indica que os nomes das colunas estão na linha 8 da planilha
    df = conn.read(spreadsheet=url_final, worksheet="LISTA ALIMENTOS", header=7)
    
    if df is not None:
        st.success("✅ Conexão estabelecida com sucesso!")
        st.subheader("Prévia dos Alimentos Carregados:")
        st.dataframe(df.head(10))

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Verifique se o nome da aba na sua planilha é exatamente: LISTA ALIMENTOS")
