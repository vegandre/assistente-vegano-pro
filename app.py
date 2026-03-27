import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* 1. ESCONDER O TEXTO 'keyboard_double' E AJUSTAR CABEÇALHO */
    header {visibility: hidden;}
    [data-testid="stSidebarNav"] {padding-top: 20px;}
    
    /* 2. FUNDO E TEXTO */
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], p, span, label { 
        font-family: 'Roboto', sans-serif !important; 
        color: #333333 !important; 
    }

    /* 3. TÍTULOS */
    h1 { color: #1B5E20 !important; font-weight: 700 !important; padding-top: 0px; }
    h2, h3 { color: #2E7D32 !important; font-weight: 700 !important; }

    /* 4. SIDEBAR (MENU LATERAL) */
    [data-testid="stSidebar"] { background-color: #1A1A1A !important; }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }

    /* 5. BOTÕES */
    .stButton>button { 
        background-color: #388E3C; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: 700; 
        width: 100%; 
        border: none;
        padding: 10px;
    }
    .stButton>button:hover { background-color: #2E7D32; border: none; }

    /* 6. MÉTRICAS E TABELAS */
    [data-testid="stMetricValue"] { color: #388E3C !important; font-size: 32px !important; font-weight: 700 !important; }
    .stTable { background-color: white; border-radius: 10px; border: 1px solid #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"
URL_ALIMENTOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"

@st.cache_data
def carregar_alimentos():
    df = pd.read_csv(URL_ALIMENTOS, header=7)
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    col_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
    for col in col_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    return df

# --- LOGIN E SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("Seu e-mail:")
    if st.button("Entrar no Painel"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    # --- BARRA LATERAL ---
    st.sidebar.markdown("### 🌱 Painel Vegano")
    st.sidebar.write(f"Usuário: \n**{st.session_state.usuario}**")
    st.sidebar.divider()
    pagina = st.sidebar.radio("Ir para:", ["🍽️ Montar Refeição", "📅 Histórico", "🔍 Alimentos"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df_ali = carregar_alimentos()

    if pagina == "🍽️ Montar Refeição":
        st.header("🍽️ Diário de Refeições")
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.subheader("➕ Adicionar")
            ali_sel = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Peso (g):", min_value=1, value=100, step=10)
            
            if st.button("Adicionar ao Prato"):
                row = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                fator = qtd / 100
                st.session_state.carrinho.append({
                    "Alimento": ali_sel,
                    "Gramas": int(qtd),
                    "Kcal": round(row['CALORIAS'] * fator, 1),
                    "Prot(g)": round(row['PROTEÍNAS'] * fator, 1)
                })
                st.toast(f"✅ {ali_sel} adicionado!")

        with col2:
            st.subheader("🛒 Resumo do Prato")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                df_exibir = df_c.copy()
                df_exibir['Kcal'] = df_exibir['Kcal'].map('{:.1f}'.format)
                df_exibir['Prot(g)'] = df_exibir['Prot(g)'].map('{:.1f}'.format)
                
                st.table(df_exibir)
                
                t_kcal = df_c['Kcal'].sum()
                t_prot = df_c['Prot(g)'].sum()
                
                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Energia", f"{t_kcal:.1f} kcal")
                c2.metric("Proteína", f"{t_prot:.1f} g")
                
                if st.button("🗑️ Limpar Tudo"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("O seu prato está vazio.")

    elif pagina == "🔍 Alimentos":
        st.header("🔍 Consulta Nutricional")
        busca = st.text_input("Buscar alimento:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
