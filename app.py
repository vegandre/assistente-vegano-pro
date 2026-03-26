import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Assistente Nutricional Vegano")

# Link de exportação direta da aba 'dados'
URL_CSV = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/export?format=csv&gid=1577491175"

try:
    # Lendo diretamente o CSV do Google Sheets
    # header=7 pula as linhas decorativas que vimos no seu print
    df = pd.read_csv(URL_CSV, header=7)
    
    if not df.empty:
        st.success("✅ DADOS CARREGADOS COM SUCESSO!")
        st.write("### Tabela de Alimentos:")
        st.dataframe(df)
    else:
        st.warning("A planilha parece estar vazia nesta aba.")

except Exception as e:
    st.error(f"Erro ao ler planilha: {e}")
    st.info("Verifique se a planilha está em 'Qualquer pessoa com o link pode ler'.")
