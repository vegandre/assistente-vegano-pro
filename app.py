import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱")

st.title("🌱 Assistente Nutricional Vegano")

# 1. Definição da URL (Cuidado extra para não haver espaços antes ou depois)
url_bruta = "https://docs.google.com/spreadsheets/d/1V_hGeCQjeVMnn0IKLRd7792kMgWxWSGr/edit#gid=1577491175"

# 2. LIMPEZA TOTAL: Remove espaços, quebras de linha e caracteres ocultos
URL_FINAL = url_bruta.strip().replace("\n", "").replace("\r", "")

try:
    # 3. Criar a conexão ignorando configurações externas problemáticas
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 4. Tentar ler a aba específica
    df = conn.read(spreadsheet=URL_FINAL, worksheet="LISTA ALIMENTOS", header=7)
    
    if df is not None:
        st.success("✅ Conexão estabelecida com sucesso!")
        st.subheader("Prévia dos Alimentos:")
        st.dataframe(df.head(10))

except Exception as e:
    st.error(f"Erro técnico detectado: {e}")
    st.info("Dica: Vá nos 'Secrets' do Streamlit e verifique se não há linhas em branco lá.")
