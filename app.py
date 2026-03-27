import streamlit as st
import pandas as pd

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .stApp { background-color: #FFFFFF; }
    h1 { color: #1B5E20 !important; font-weight: 700 !important; }
    h2, h3 { color: #2E7D32 !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] { background-color: #1A1A1A !important; }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }
    .stButton>button { background-color: #388E3C; color: white !important; border-radius: 8px; font-weight: 700; width: 100%; border: none; padding: 12px; }
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
        # Padronização de nomes para evitar erros de busca (KeyError)
        df.columns = df.columns.str.strip().str.upper()
        cols_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

# --- 3. CONTROLE DE SESSÃO (RESET SEGURO) ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# Forçamos a atualização do dicionário de metas para evitar o KeyError
metas_padrao = {"kcal": 3000, "prot": 100, "carb": 300, "gord": 110, "fibra": 40, "get": 0}
if 'metas' not in st.session_state:
    st.session_state.metas = metas_padrao
else:
    # Garante que novas chaves existam mesmo em sessões antigas
    for k, v in metas_padrao.items():
        if k not in st.session_state.metas:
            st.session_state.metas[k] = v

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
    st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario}")
    pagina = st.sidebar.radio("Navegação:", ["👤 Meu Perfil (TMB)", "🍽️ Diário de Refeições", "🔍 Banco de Alimentos"])
    
    df_ali = carregar_alimentos()

    if pagina == "👤 Meu Perfil (TMB)":
        st.header("👤 Perfil & Metabolismo")
        col_corporal, col_metas = st.columns(2)
        
        with col_corporal:
            st.subheader("1. Dados Corporais")
            peso = st.number_input("Peso (kg):", value=68.0, step=0.1)
            altura = st.number_input("Altura (cm):", value=154.0, step=1.0)
            idade = st.number_input("Idade:", value=20, step=1)
            sexo = st.selectbox("Sexo Biológico:", ["MASCULINO", "FEMININO"])
            
            # Cálculo Exato da sua Planilha
            if sexo == "MASCULINO":
                tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
            else:
                tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)
            
            st.info(f"Sua TMB Base: **{tmb:.2f} kcal**")

            st.divider()
            st.subheader("2. Nível de Atividade")
            fatores = {"SEDENTÁRIO": 1.2, "LEVEMENTE ATIVO": 1.38, "MODERADAMENTE ATIVO": 1.55, "MUITO ATIVO": 1.73, "EXTREMAMENTE ATIVO": 1.9}
            nivel = st.selectbox("Selecione seu nível:", options=list(fatores.keys()))
            st.session_state.metas["get"] = tmb * fatores[nivel]
            st.success(f"Gasto Total Diário (GET): **{st.session_state.metas['get']:.2f} kcal**")

        with col_metas:
            st.subheader("3. Defina Suas Metas Manuais")
            st.session_state.metas["kcal"] = st.number_input("Meta Calorias (kcal):", value=st.session_state.metas["kcal"])
            st.session_state.metas["prot"] = st.number_input("Meta Proteínas (g):", value=st.session_state.metas["prot"])
            st.session_state.metas["carb"] = st.number_input("Meta Carboidratos (g):", value=st.session_state.metas["carb"])
            st.session_state.metas["gord"] = st.number_input("Meta Gorduras (g):", value=st.session_state.metas["gord"])
            st.session_state.metas["fibra"] = st.number_input("Meta Fibras (g):", value=st.session_state.metas["fibra"])
            
            dif = st.session_state.metas["kcal"] - st.session_state.metas["get"]
            st.markdown(f"""
            > **Resumo do Plano:**
            > Comparação entre sua **Meta Manual** e seu **Gasto Real (GET)**.
            > - **Saldo Calórico:** {dif:+.2f} kcal
            > - **Proteína/kg:** {st.session_state.metas['prot']/peso:.2f} g/kg
            """)

    elif pagina == "🍽️ Diário de Refeições":
        st.header("🍽️ Diário de Refeições")
        col1, col2 = st.columns([1, 1.3])
        
        with col1:
            st.subheader("➕ Adicionar")
            if not df_ali.empty:
                ali_sel = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
                qtd = st.number_input("Quantidade (g):", min_value=1, value=100)
                if st.button("Adicionar ao Prato"):
                    row = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                    f = qtd / 100
                    st.session_state.carrinho.append({
                        "Alimento": ali_sel, "Gramas": int(qtd),
                        "Kcal": row['CALORIAS'] * f, "Prot": row['PROTEÍNAS'] * f,
                        "Carb": row['CARBOIDRATOS'] * f, "Gord": row['GORDURAS'] * f, "Fib": row['FIBRA'] * f
                    })
                    st.rerun()

        with col2:
            st.subheader("🛒 Consumo de Hoje")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                st.dataframe(df_c[['Alimento', 'Gramas', 'Kcal', 'Prot']], use_container_width=True, hide_index=True)
                
                t = df_c.sum(numeric_only=True)
                st.divider()
                c = st.columns(3)
                c[0].metric("Calorias", f"{t['Kcal']:.0f}", f"{st.session_state.metas['kcal'] - t['Kcal']:.0f} restam")
                c[1].metric("Proteínas", f"{t['Prot']:.1f}g", f"{st.session_state.metas['prot'] - t['Prot']:.1f}g restam")
                c[2].metric("Carbos", f"{t['Carb']:.1f}g", f"{st.session_state.metas['carb'] - t['Carb']:.1f}g restam")
                
                if st.button("🗑️ Limpar"):
                    st.session_state.carrinho = []
                    st.rerun()

    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Banco de Alimentos")
        busca = st.text_input("Filtrar alimento:")
        df_f = df_ali.copy()
        if busca: df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
