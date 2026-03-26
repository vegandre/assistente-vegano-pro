import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")

st.title("🌱 Assistente Nutricional Vegano")

# 2. URL da planilha - Limpando caracteres invisíveis automaticamente
URL_ORIGINAL = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"
URL_LIMPA = URL_ORIGINAL.strip()

try:
    # 3. Estabelecendo a conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 4. Lendo os dados da aba específica
    # O parâmetro header=7 indica que os títulos estão na linha 8 do Excel (índice 7 no Python)
    df = conn.read(spreadsheet=URL_LIMPA, worksheet="LISTA ALIMENTOS", header=7)
    
    # 5. Exibindo mensagem de sucesso e os dados
    st.success("✅ Conexão estabelecida com sucesso!")
    st.subheader("Visualização dos dados da planilha:")
    st.dataframe(df.head(10))

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Dica: Verifique se o nome da aba na planilha é exatamente 'LISTA ALIMENTOS' e se ela está compartilhada corretamente.")
