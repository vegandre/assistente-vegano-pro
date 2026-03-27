import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;} 
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], p, span, label { font-family: 'Roboto', sans-serif !important; color: #333333 !important; }
    h1 { color: #1B5E20 !important; }
    h2, h3 { color: #2E7D32 !important; }
    [data-testid="stSidebar"] { background-color: #1A1A1A !important; }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }
    .stButton>button { background-color: #388E3C; color: white !important; border-radius: 8px; font-weight: 700; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
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

# --- INICIALIZAÇÃO DE VARIÁVEIS ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'perfil' not in st.session_state: 
    st.session_state.perfil = {"tmb": 0, "meta_kcal": 2000, "meta_prot": 120}

# --- LOGIN ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail para acesso:")
    if st.button("Entrar"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    # --- SIDEBAR ---
    st.sidebar.title("🌱 Menu")
    pagina = st.sidebar.radio("Navegar para:", ["👤 Meu Perfil", "🍽️ Montar Refeição", "🔍 Banco de Alimentos"])
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df_ali = carregar_alimentos()

    # --- ABA: MEU PERFIL (RAIO-X) ---
    if pagina == "👤 Meu Perfil":
        st.header("👤 Raio-X do Perfil Nutricional")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Seus Dados")
            peso = st.number_input("Peso (kg):", value=70.0)
            altura = st.number_input("Altura (cm):", value=170.0)
            idade = st.number_input("Idade:", value=25)
            sexo = st.selectbox("Sexo:", ["Masculino", "Feminino"])
            
            # Cálculo TMB (Harris-Benedict)
            if sexo == "Masculino":
                tmb = 66 + (13.7 * peso) + (5 * altura) - (6.8 * idade)
            else:
                tmb = 655 + (9.6 * peso) + (1.8 * altura) - (4.7 * idade)
            
            st.session_state.perfil["tmb"] = tmb
            st.metric("Sua TMB (Gasto em Repouso)", f"{tmb:.0f} kcal")

        with col2:
            st.subheader("Minhas Metas Diárias")
            st.session_state.perfil["meta_kcal"] = st.number_input("Meta de Calorias (kcal):", value=2500)
            st.session_state.perfil["meta_prot"] = st.number_input("Meta de Proteína (g):", value=150)
            st.info("Esses valores serão usados para comparar com o seu consumo no diário.")

    # --- ABA: MONTAR REFEIÇÃO ---
    elif pagina == "🍽️ Montar Refeição":
        st.header("🍽️ Diário de Refeições")
        
        # Seletor de Tipo de Refeição
        tipo_ref = st.selectbox("Qual refeição você está fazendo?", 
                                ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"])
        
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.subheader("➕ Adicionar Alimento")
            ali_sel = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (g):", min_value=1, value=100)
            
            if st.button("Adicionar ao Prato"):
                row = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                f = qtd / 100
                st.session_state.carrinho.append({
                    "Refeição": tipo_ref,
                    "Alimento": ali_sel,
                    "Grams": int(qtd),
                    "Kcal": row['CALORIAS'] * f,
                    "Prot": row['PROTEÍNAS'] * f,
                    "Carb": row['CARBOIDRATOS'] * f,
                    "Gord": row['GORDURAS'] * f
                })
                st.toast(f"✅ {ali_sel} adicionado ao {tipo_ref}!")

        with col2:
            st.subheader("🛒 Resumo do Dia")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                st.dataframe(df_c, hide_index=True)
                
                totais = df_c.sum(numeric_only=True)
                
                st.divider()
                # Comparação com metas do perfil
                c1, c2 = st.columns(2)
                prog_kcal = totais['Kcal'] / st.session_state.perfil['meta_kcal']
                prog_prot = totais['Prot'] / st.session_state.perfil['meta_prot']
                
                c1.metric("Energia Total", f"{totais['Kcal']:.0f} kcal", 
                          f"{st.session_state.perfil['meta_kcal'] - totais['Kcal']:.0f} restante")
                c2.metric("Proteína Total", f"{totais['Prot']:.1f} g",
                          f"{st.session_state.perfil['meta_prot'] - totais['Prot']:.1f} g restante")
                
                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Adicione alimentos para ver o progresso das suas metas.")

    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Consulta de Nutrientes")
        busca = st.text_input("Pesquise um alimento (ex: Soja, Aveia...):")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
