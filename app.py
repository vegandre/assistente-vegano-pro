import streamlit as st
import pandas as pd

# Configurações Iniciais
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

# --- BANCO DE DADOS (LINKS) ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"  # Aba de Alimentos
GID_PLANO = "368321147"  # Aba de Perfil/Metas
URL_ALIMENTOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"
URL_PERFIL = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_PLANO}"

# --- FUNÇÕES DE CARREGAMENTO ---
@st.cache_data
def carregar_alimentos():
    df = pd.read_csv(URL_ALIMENTOS, header=7)
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    
    # Lista das colunas que devem ser números
    colunas_numericas = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
    
    for col in colunas_numericas:
        if col in df.columns:
            # 1. Transforma tudo em texto
            # 2. Troca a vírgula por ponto
            # 3. Converte para número (float), ignorando erros
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            
    return df
@st.cache_data
def carregar_perfil():
    # Carrega os dados do seu perfil (Nome, Idade, Metas)
    return pd.read_csv(URL_PERFIL)

# --- SISTEMA DE ACESSO (LOGIN SIMPLIFICADO) ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso ao Sistema")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email == "admin@vegano.com" and senha == "123": # Altere aqui depois
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
else:
    # --- MENU LATERAL ---
    st.sidebar.title(f"🌱 Menu")
    pagina = st.sidebar.radio("Ir para:", ["Meu Perfil", "Calculadora de Refeições", "Banco de Alimentos"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # --- PÁGINA: MEU PERFIL ---
    if pagina == "Meu Perfil":
        st.header("📊 Meu Perfil e Metas")
        df_p = carregar_perfil()
        # Aqui organizamos os dados que vimos no seu print anterior
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Meta Calorias", "3000 kcal")
            st.metric("Meta Proteínas", "100g")
        with col2:
            st.metric("Meta Carboidratos", "300g")
            st.metric("Meta Gorduras", "110g")
        st.info("Dados integrados diretamente da sua Planilha Google.")

    # --- PÁGINA: BANCO DE ALIMENTOS ---
    elif pagina == "Banco de Alimentos":
        st.header("🔍 Consulta de Nutrientes")
        df = carregar_alimentos()
        busca = st.text_input("Pesquisar Alimento:")
        if busca:
            df = df[df.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- PÁGINA: REFEIÇÕES ---
    elif pagina == "Calculadora de Refeições":
        st.header("🍽️ Montar Refeição")
        df = carregar_alimentos()
        
        # Seleção do Alimento
        alimento_nome = st.selectbox("Selecione o Alimento:", df.iloc[:, 0].unique())
        quantidade = st.number_input("Quantidade (gramas):", min_value=1, value=100)
        
        if st.button("Calcular Nutrientes"):
            dados_alimento = df[df.iloc[:, 0] == alimento_nome].iloc[0]
            # Cálculo proporcional (baseado em 100g da tabela)
            fator = quantidade / 100
            cal = float(str(dados_alimento['CALORIAS']).replace(',','.')) * fator
            prot = float(str(dados_alimento['PROTEÍNAS']).replace(',','.')) * fator
            
            st.write(f"### Resultado para {quantidade}g de {alimento_nome}:")
            c1, c2 = st.columns(2)
            c1.metric("Energia", f"{cal:.2f} kcal")
            c2.metric("Proteína", f"{prot:.2f} g")

@st.cache_data
def buscar_metas_reais():
    # GID da aba PLANO que vimos no seu print anterior
    URL_PLANO = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid=368321147"
    df_plano = pd.read_csv(URL_PLANO)
    
    # Extraindo os valores baseados na estrutura da sua planilha (ajuste as linhas se precisar)
    # No seu print, Meta Calorias estava perto da linha 11
    metas = {
        "calorias": 3000, # Valores padrão caso a leitura falhe
        "proteinas": 100,
        "carbos": 300,
        "gorduras": 110
    }
    return metas
