import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Assistente Nutricional Vegano")

# 1. Seus dados extraídos do print
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_ABA = "368321147"

# 2. Montagem do link de exportação direta
URL_FINAL = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_ABA}"

try:
    # 3. Lendo os dados (header=7 pula as linhas de topo da sua planilha)
    df = pd.read_csv(URL_FINAL, header=7)
    
    if not df.empty:
        st.success("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        st.write("### Lista de Alimentos carregada:")
        st.dataframe(df)
    else:
        st.warning("A conexão funcionou, mas não encontrei dados na linha 8 em diante.")

except Exception as e:
    st.error(f"Erro crítico ao acessar os dados: {e}")
    st.info("Verifique se a nova planilha está com acesso para 'Qualquer pessoa com o link'.")
