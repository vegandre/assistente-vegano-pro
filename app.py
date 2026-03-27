import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f9f4; }
    /* Ajuste de cor dos títulos para melhor contraste */
    h1, h2, h3, p, span, label { color: #1b5e20 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 8px; font-weight: bold; }
    /* Estilização dos cards de métricas */
    [data-testid="stMetricValue"] { color: #2e7d32 !important; font-size: 24px; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #558b2f !important; }
    .stTable { background-color: white; border-radius: 10px; }
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

# --- SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail:")
    if st.button("Acessar Painel"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    # --- MENU LATERAL ---
    st.sidebar.markdown("# 🌱 Painel Vegano")
    st.sidebar.write(f"Conectado: **{st.session_state.usuario}**")
    pagina = st.sidebar.radio("Navegação:", ["🍽️ Montar Refeição", "📅 Histórico", "🔍 Banco de Alimentos"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df_ali = carregar_alimentos()

    if pagina == "🍽️ Montar Refeição":
        st.header("🍽️ Diário de Refeições")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Adicionar Alimento")
            ali_sel = st.selectbox("Escolha o alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (g):", min_value=1, value=100)
            
            if st.button("Adicionar ao Prato"):
                row = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                fator = qtd / 100
                # Arredondando para 1 casa decimal para ficar limpo
                st.session_state.carrinho.append({
                    "Alimento": ali_sel,
                    "Gramas": int(qtd),
                    "Kcal": round(row['CALORIAS'] * fator, 1),
                    "Prot(g)": round(row['PROTEÍNAS'] * fator, 1)
                })
                st.toast(f"✅ {ali_sel} adicionado!")

        with col2:
            st.subheader("🛒 Itens Selecionados")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                st.table(df_c)
                
                t_kcal = df_c['Kcal'].sum()
                t_prot = df_c['Prot(g)'].sum()
                
                c1, c2 = st.columns(2)
                c1.metric("Energia Total", f"{t_kcal:.1f} kcal")
                c2.metric("Proteína Total", f"{t_prot:.1f} g")
                
                if st.button("🗑️ Limpar"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("O prato está vazio.")

    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Banco de Alimentos")
        busca = st.text_input("Pesquisar:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
