import streamlit as st
import pandas as pd

# --- 1. CONFIGURAÇÃO VISUAL PROFISSIONAL ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], p, span, label { 
        font-family: 'Roboto', sans-serif !important; 
        color: #333333 !important; 
    }

    h1 { color: #1B5E20 !important; font-weight: 700 !important; }
    h2, h3 { color: #2E7D32 !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] { background-color: #1A1A1A !important; }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }

    .stButton>button { 
        background-color: #388E3C; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: 700; 
        width: 100%; 
        border: none;
        padding: 12px;
    }
    .stButton>button:hover { background-color: #2E7D32; }

    [data-testid="stMetricValue"] { color: #388E3C !important; font-size: 32px !important; font-weight: 700 !important; }
    div[data-testid="stMarkdownContainer"] > blockquote { border-left: 5px solid #2e7d32; background-color: #f1f8e9; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACESSO AOS DADOS ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"
URL_ALIMENTOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"

@st.cache_data
def carregar_alimentos():
    try:
        df = pd.read_csv(URL_ALIMENTOS, header=7)
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        cols_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

# --- 3. CONTROLE DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'perfil' not in st.session_state: 
    st.session_state.perfil = {"tmb": 0, "get": 0, "meta_kcal": 0, "meta_prot": 0}

# --- 4. TELA DE LOGIN ---
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
    st.sidebar.markdown("# 🌱 Painel")
    pagina = st.sidebar.radio("Navegação:", ["👤 Meu Perfil (TMB)", "🍽️ Diário de Refeições", "🔍 Banco de Alimentos"])
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA: MEU PERFIL ---
    if pagina == "👤 Meu Perfil (TMB)":
        st.header("👤 Perfil & Metabolismo")
        col_corporal, col_metas = st.columns(2)
        
        with col_corporal:
            st.subheader("1. Dados Corporais")
            peso = st.number_input("Peso (kg):", value=70.0, step=0.1)
            altura = st.number_input("Altura (cm):", value=170.0, step=1.0)
            idade = st.number_input("Idade:", value=25, step=1)
            sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
            
            # Mifflin-St Jeor
            if sexo == "Masculino":
                tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
            else:
                tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
            
            st.session_state.perfil["tmb"] = tmb_base
            st.info(f"Sua TMB Base: **{tmb_base:.0f} kcal**")

            st.divider()
            st.subheader("2. Nível de Atividade")
            
            # Multiplicadores Exatos solicitados
            fatores = {
                "Sedentário": 1.2,
                "Levemente ativo": 1.38,
                "Moderadamente ativo": 1.55,
                "Muito ativo": 1.73,
                "Extremamente ativo": 1.9
            }
            
            nivel = st.selectbox("Selecione seu nível:", options=list(fatores.keys()))
            gasto_total = tmb_base * fatores[nivel]
            st.session_state.perfil["get"] = gasto_total
            
            st.success(f"Seu Gasto Diário Estimado (GET): **{gasto_total:.0f} kcal**")

        with col_metas:
            st.subheader("3. Defina Suas Metas (Manual)")
            
            # Inputs manuais sem sugestão automática
            st.session_state.perfil["meta_kcal"] = st.number_input(
                "Sua Meta de Calorias (kcal):", 
                value=int(st.session_state.perfil["meta_kcal"]),
                step=50
            )
            
            st.session_state.perfil["meta_prot"] = st.number_input(
                "Sua Meta de Proteínas (g):", 
                value=int(st.session_state.perfil["meta_prot"]),
                step=1
            )
            
            if st.session_state.perfil["meta_kcal"] > 0:
                dif = st.session_state.perfil["meta_kcal"] - gasto_total
                st.markdown(f"""
                > **Resumo do Plano:**
                > - **Diferença para o GET:** {dif:+.0f} kcal
                > - **Proteína/kg:** {st.session_state.perfil['meta_prot']/peso:.1f} g/kg
                """)

    # --- PÁGINA: DIÁRIO ---
    elif pagina == "🍽️ Diário de Refeições":
        st.header("🍽️ Diário de Refeições")
        tipo_ref = st.selectbox("Qual refeição?", ["Café da Manhã", "Lanche", "Almoço", "Jantar", "Ceia"])
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.subheader("➕ Adicionar Alimento")
            ali_sel = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (g):", min_value=1, value=100)
            
            if st.button("Adicionar ao Prato"):
                dados = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                f = qtd / 100
                st.session_state.carrinho.append({
                    "Refeição": tipo_ref, "Alimento": ali_sel, "Gramas": int(qtd),
                    "Kcal": round(dados['CALORIAS'] * f, 1), "Prot": round(dados['PROTEÍNAS'] * f, 1)
                })
                st.rerun()

        with col2:
            st.subheader("🛒 Resumo do Dia")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                st.dataframe(df_c, use_container_width=True, hide_index=True)
                
                total_k = df_c['Kcal'].sum()
                total_p = df_c['Prot'].sum()
                
                st.divider()
                m1, m2 = st.columns(2)
                mk = st.session_state.perfil['meta_kcal']
                mp = st.session_state.perfil['meta_prot']
                
                m1.metric("Kcal Totais", f"{total_k:.0f}", f"{mk - total_k:.0f} faltam" if mk > 0 else None)
                m2.metric("Proteína Total", f"{total_p:.1f}g", f"{mp - total_p:.1f}g faltam" if mp > 0 else None)
                
                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Diário vazio.")

    # --- PÁGINA: BANCO ---
    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Consulta")
        busca = st.text_input("Pesquisar:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
