import streamlit as st
import pandas as pd

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    page_title="Assistente Vegano Pro", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #1B5E20 !important; }
    label { color: #1B5E20 !important; font-weight: bold; }
    .stButton>button { background-color: #388E3C; color: white; border-radius: 8px; width: 100%; }
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
        # Tratamento numérico
        cols_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'metas' not in st.session_state:
    st.session_state.metas = {"kcal": 3100, "prot": 200, "carb": 300, "gord": 110, "fibra": 40, "get": 0}

# --- 4. LÓGICA DE NAVEGAÇÃO ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail cadastrado:")
    if st.button("Acessar Painel"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    with st.sidebar:
        st.title("🌱 Menu")
        st.write(f"**Usuário:** {st.session_state.usuario}")
        pagina = st.radio("Navegação:", ["👤 Perfil & Metas", "🍽️ Diário Alimentar", "🔍 Banco de Dados"])
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA PERFIL ---
    if pagina == "👤 Perfil & Metas":
        st.header("👤 Perfil & Metabolismo")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Seus Dados")
            peso = st.number_input("Peso (kg)", value=68.0, step=0.1)
            altura = st.number_input("Altura (cm)", value=154.0, step=1.0)
            idade = st.number_input("Idade", value=20)
            sexo = st.selectbox("Sexo Biológico", ["MASCULINO", "FEMININO"])
            
            # Fórmula Harris-Benedict (Revisada)
            if sexo == "MASCULINO":
                tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
            else:
                tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)
            
            st.info(f"TMB Base: {tmb:.2f} kcal")
            fatores = {"SEDENTÁRIO": 1.2, "LEVEMENTE ATIVO": 1.38, "MODERADAMENTE ATIVO": 1.55, "MUITO ATIVO": 1.73, "EXTREMAMENTE ATIVO": 1.9}
            nivel = st.selectbox("Nível de Atividade:", list(fatores.keys()))
            st.session_state.metas["get"] = tmb * fatores[nivel]
            st.success(f"Gasto Diário (GET): {st.session_state.metas['get']:.2f} kcal")

        with col2:
            st.subheader("Definição de Metas")
            st.session_state.metas["kcal"] = st.number_input("Meta Calorias", value=st.session_state.metas["kcal"])
            st.session_state.metas["prot"] = st.number_input("Meta Proteínas (g)", value=st.session_state.metas["prot"])
            st.session_state.metas["carb"] = st.number_input("Meta Carboidratos (g)", value=st.session_state.metas["carb"])
            st.session_state.metas["gord"] = st.number_input("Meta Gorduras (g)", value=st.session_state.metas["gord"])
            st.session_state.metas["fibra"] = st.number_input("Meta Fibras (g)", value=st.session_state.metas["fibra"])

    # --- PÁGINA DIÁRIO (ATUALIZADA) ---
    elif pagina == "🍽️ Diário Alimentar":
        st.header("🍽️ Diário de Refeições")
        
        col_add, col_resumo = st.columns([1, 1.5])
        
        with col_add:
            st.subheader("➕ Adicionar Alimento")
            refeicao = st.selectbox("Qual a refeição?", ["Café da Manhã", "Almoço", "Lanche", "Jantar", "Ceia"])
            
            if not df_ali.empty:
                alimento_nome = st.selectbox("Selecione o Alimento:", df_ali.iloc[:, 0].unique())
                quantidade = st.number_input("Quantidade (g):", min_value=1, value=100)
                
                if st.button("Lançar no Diário"):
                    dados_ali = df_ali[df_ali.iloc[:, 0] == alimento_nome].iloc[0]
                    fator = quantidade / 100
                    
                    novo_item = {
                        "Refeição": refeicao,
                        "Alimento": alimento_nome,
                        "Peso": quantidade,
                        "Kcal": dados_ali['CALORIAS'] * fator,
                        "Prot": dados_ali['PROTEÍNAS'] * fator,
                        "Carb": dados_ali['CARBOIDRATOS'] * fator,
                        "Gord": dados_ali['GORDURAS'] * fator
                    }
                    st.session_state.carrinho.append(novo_item)
                    st.rerun()

        with col_resumo:
            st.subheader("📊 Resumo do Dia")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                # Mostra a tabela organizada por refeição
                st.dataframe(df_c[["Refeição", "Alimento", "Peso", "Kcal", "Prot"]], use_container_width=True, hide_index=True)
                
                totais = df_c.sum(numeric_only=True)
                st.divider()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Kcal Totais", f"{totais['Kcal']:.0f}", f"{st.session_state.metas['kcal'] - totais['Kcal']:.0f} restam")
                m2.metric("Proteínas", f"{totais['Prot']:.1f}g", f"{st.session_state.metas['prot'] - totais['Prot']:.1f}g restam")
                m3.metric("Carbos", f"{totais['Carb']:.1f}g", f"{st.session_state.metas['carb'] - totais['Carb']:.1f}g restam")
                
                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Nenhum alimento lançado hoje.")

    # --- PÁGINA BANCO ---
    elif pagina == "🔍 Banco de Dados":
        st.header("🔍 Consulta de Alimentos")
        busca = st.text_input("Filtrar por nome:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
