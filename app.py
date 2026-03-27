import streamlit as st
import pandas as pd

# --- 1. CONFIGURAÇÃO DE PÁGINA (A PRIMEIRA COISA DO CÓDIGO) ---
st.set_page_config(
    page_title="Assistente Vegano Pro", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded" # Força a barra aberta
)

# --- 2. CSS SIMPLIFICADO (SEM BLOQUEAR INTERFACE) ---
st.markdown("""
    <style>
    /* Apenas cores e fontes, sem esconder headers ou sidebars */
    h1, h2, h3 { color: #1B5E20 !important; }
    label { color: #1B5E20 !important; font-weight: bold; }
    .stButton>button { background-color: #388E3C; color: white; border-radius: 8px; }
    div[data-testid="stMarkdownContainer"] > blockquote { 
        border-left: 5px solid #2e7d32; 
        background-color: #f1f8e9; 
        padding: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS E SESSÃO ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"
URL_ALIMENTOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"

@st.cache_data
def carregar_alimentos():
    try:
        df = pd.read_csv(URL_ALIMENTOS, header=7)
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = df.columns.str.strip().str.upper()
        return df
    except: return pd.DataFrame()

if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'metas' not in st.session_state:
    st.session_state.metas = {"kcal": 3100, "prot": 200, "carb": 300, "gord": 110, "fibra": 40, "get": 0}

# --- 4. LÓGICA DE TELAS ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail:")
    if st.button("Acessar"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    # --- BARRA LATERAL (FORÇADA) ---
    with st.sidebar:
        st.title("🌱 Menu")
        st.write(f"Usuário: {st.session_state.usuario}")
        pagina = st.radio("Navegação:", ["👤 Perfil", "🍽️ Diário", "🔍 Alimentos"])
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    df_ali = carregar_alimentos()

    if pagina == "👤 Perfil":
        st.header("👤 Perfil & Metabolismo")
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso (kg)", value=68.0)
            altura = st.number_input("Altura (cm)", value=154.0)
            idade = st.number_input("Idade", value=20)
            sexo = st.selectbox("Sexo", ["MASCULINO", "FEMININO"])
            tmb = (88.36 + (13.4*peso) + (4.8*altura) - (5.7*idade)) if sexo == "MASCULINO" else (447.6 + (9.2*peso) + (3.1*altura) - (4.3*idade))
            st.info(f"TMB: {tmb:.2f}")
            fatores = {"SEDENTÁRIO": 1.2, "LEVEMENTE ATIVO": 1.38, "MODERADAMENTE ATIVO": 1.55, "MUITO ATIVO": 1.73, "EXTREMAMENTE ATIVO": 1.9}
            nivel = st.selectbox("Atividade:", list(fatores.keys()))
            st.session_state.metas["get"] = tmb * fatores[nivel]
        with col2:
            st.session_state.metas["kcal"] = st.number_input("Meta Kcal", value=st.session_state.metas["kcal"])
            st.session_state.metas["prot"] = st.number_input("Meta Proteína", value=st.session_state.metas["prot"])
            st.session_state.metas["carb"] = st.number_input("Meta Carboidrato", value=st.session_state.metas["carb"])
            st.session_state.metas["gord"] = st.number_input("Meta Gordura", value=st.session_state.metas["gord"])
            st.session_state.metas["fibra"] = st.number_input("Meta Fibra", value=st.session_state.metas["fibra"])

    elif pagina == "🍽️ Diário":
        st.header("🍽️ Diário")
        if not df_ali.empty:
            ali = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Grams:", value=100)
            if st.button("Adicionar"):
                st.session_state.carrinho.append({"Alimento": ali, "Kcal": 100}) # Simplificado para teste
                st.success("Adicionado!")

    elif pagina == "🔍 Alimentos":
        st.header("🔍 Banco de Dados")
        st.dataframe(df_ali)
