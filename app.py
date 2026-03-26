import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")
st.title("🌱 Assistente Nutricional Vegano")

# 1. Seus dados confirmados pelo print
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175" 

URL_FINAL = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"

try:
    # 2. Lendo a partir da linha 8 (header=7 no Python)
    # Como os dados começam na coluna G, vamos remover as colunas vazias automagicamente
    df = pd.read_csv(URL_FINAL, header=7)
    
    # Limpeza: remove colunas e linhas totalmente vazias
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    
    st.success("✅ TABELA DE ALIMENTOS CARREGADA!")

    # 3. Barra de Busca
    busca = st.text_input("🔍 Pesquisar alimento (ex: Aveia, Banana...):")
    
    if busca:
        # Filtra na primeira coluna (ALIMENTO)
        df_filtrado = df[df.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar a tabela: {e}")
