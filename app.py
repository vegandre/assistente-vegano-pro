import streamlit as st
import pandas as pd

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], p, span, label { font-family: 'Roboto', sans-serif !important; color: #333333 !important; }
    h1 { color: #1B5E20 !important; font-weight: 700 !important; }
    h2, h3 { color: #2E7D32 !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] { background-color: #1A1A1A !important; }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }
    .stButton>button { background-color: #388E3C; color: white !important; border-radius: 8px; font-weight: 700; width: 100%; border: none; padding: 10px; }
    .stButton>button:hover { background-color: #2E7D32; }
    [data-testid="stMetricValue"] { color: #388E3C !important; font-size: 32px !important; font-weight: 700 !important; }
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
        cols = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

# --- 3. CONTROLE DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'perfil' not in st.session_state: 
    st.session_state.perfil = {"tmb": 0, "get": 0, "meta_kcal": 2000, "meta_prot": 120}

# --- 4. LÓGICA DE ACESSO ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail:")
    if st.button("Acessar Sistema"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    st.sidebar.markdown("## 🌱 Menu Principal")
    pagina = st.sidebar.radio("Ir para:", ["👤 Meu Perfil (Raio-X)", "🍽️ Diário de Refeições", "🔍 Banco de Alimentos"])
    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.carrinho = []
        st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA: MEU PERFIL (CÁLCULO TMB CORRIGIDO) ---
    if pagina == "👤 Meu Perfil (Raio-X)":
        st.header("👤 Perfil Nutricional & Metabolismo")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Seus Dados Corporais")
            peso = st.number_input("Peso (kg):", value=75.0, step=0.1)
            altura = st.number_input("Altura (cm):", value=175.0, step=1.0)
            idade = st.number_input("Idade:", value=30, step=1)
            sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
            
            # FÓRMULA DE MIFFLIN-ST JEOR
            if sexo == "Masculino":
                tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
            else:
                tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
            
            st.divider()
            st.subheader("Nível de Atividade")
            nivel = st.select_slider(
                "Frequência de exercícios:",
                options=["Sedentário", "Leve", "Moderado", "Ativo", "Atleta"],
                value="Moderado"
            )
            
            fatores = {"Sedentário": 1.2, "Leve": 1.375, "Moderado": 1.55, "Ativo": 1.725, "Atleta": 1.9}
            gasto_total = tmb_base * fatores[nivel]
            
            st.session_state.perfil["tmb"] = tmb_base
            st.session_state.perfil["get"] = gasto_total
            
            st.info(f"Sua TMB Base: **{tmb_base:.0f} kcal**")
            st.success(f"Seu Gasto Diário Estimado (GET): **{gasto_total:.0f} kcal**")

        with c2:
            st.subheader("Definição de Metas")
            objetivo = st.radio("Qual seu objetivo?", ["Perder Peso", "Manter Peso", "Ganhar Massa"])
            
            if objetivo == "Perder Peso":
                sug_kcal = gasto_total - 500
            elif objetivo == "Ganhar Massa":
                sug_kcal = gasto_total + 300
            else:
                sug_kcal = gasto_total
                
            st.session_state.perfil["meta_kcal"] = st.number_input("Meta Diária de Calorias (kcal):", value=int(sug_kcal))
            st.session_state.perfil["meta_prot"] = st.number_input("Meta Diária de Proteínas (g):", value=int(peso * 1.8))
            
            st.markdown(f"""
            > **Estratégia Atual:**
            > - **Foco:** {objetivo}
            > - **Déficit/Superávit:** {st.session_state.perfil['meta_kcal'] - gasto_total:.0f} kcal
            """)

    # --- PÁGINA: DIÁRIO ---
    elif pagina == "🍽️ Diário de Refeições":
        st.header("🍽️ Montar Refeição")
        tipo_ref = st.selectbox("Refeição atual:", ["Café da Manhã", "Almoço", "Lanche", "Jantar", "Ceia"])
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.subheader("➕ Adicionar")
            ali_sel = st.selectbox("Escolha o alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (g):", min_value=1, value=100)
            if st.button("Adicionar ao Prato"):
                row = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                f = qtd / 100
                st.session_state.carrinho.append({
                    "Refeição": tipo_ref, "Alimento": ali_sel, "Gramas": int(qtd),
                    "Kcal": round(row['CALORIAS'] * f, 1), "Prot": round(row['PROTEÍNAS'] * f, 1)
                })
                st.rerun()

        with col2:
            st.subheader("🛒 Resumo do Dia")
            if st.session_state.carrinho:
                try:
                    df_c = pd.DataFrame(st.session_state.carrinho)
                    st.dataframe(df_c, use_container_width=True, hide_index=True)
                    
                    if 'Kcal' in df_c.columns:
                        total_k = df_c['Kcal'].sum()
                        total_p = df_c['Prot'].sum()
                        
                        st.divider()
                        m1, m2 = st.columns(2)
                        meta_k = st.session_state.perfil['meta_kcal']
                        meta_p = st.session_state.perfil['meta_prot']
                        m1.metric("Energia", f"{total_k:.0f} kcal", f"{meta_k - total_k:.0f} restante")
                        m2.metric("Proteína", f"{total_p:.1f} g", f"{meta_p - total_p:.1f} g restante")
                except:
                    st.session_state.carrinho = []
                    st.rerun()
                
                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Diário vazio.")

    # --- PÁGINA: BANCO DE ALIMENTOS ---
    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Consulta")
        busca = st.text_input("Pesquisar:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
