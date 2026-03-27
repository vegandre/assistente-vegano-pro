import streamlit as st
import pandas as pd

# --- 1. CONFIGURAÇÃO VISUAL PROFISSIONAL ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    /* Ocultar cabeçalho do Streamlit */
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* Fontes e Fundo */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"], p, span, label { 
        font-family: 'Roboto', sans-serif !important; 
        color: #333333 !important; 
    }

    /* Títulos e Menu */
    h1 { color: #1B5E20 !important; font-weight: 700 !important; padding-top: 0px; margin-bottom: 20px !important;}
    h2, h3 { color: #2E7D32 !important; font-weight: 700 !important; margin-top: 15px !important;}
    [data-testid="stSidebar"] { background-color: #1A1A1A !important; }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }

    /* Botões */
    .stButton>button { 
        background-color: #388E3C; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: 700; 
        width: 100%; 
        border: none;
        padding: 12px;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #2E7D32; }

    /* Métricas e Informativos */
    [data-testid="stMetricValue"] { color: #388E3C !important; font-size: 32px !important; font-weight: 700 !important; }
    div[data-testid="stMarkdownContainer"] > blockquote { border-left: 5px solid #2e7d32; background-color: #f1f8e9; padding: 10px 15px; border-radius: 5px; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACESSO AOS DADOS (PLANILHA) ---
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
    # Inicializa com valores zerados para o usuário definir
    st.session_state.perfil = {"tmb": 0, "get": 0, "meta_kcal": 0, "meta_prot": 0}

# --- 4. TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    st.write("### Identifique-se para acessar seu painel.")
    
    with st.container():
        email = st.text_input("Digite seu e-mail:")
        if st.button("Acessar Painel"):
            if "@" in email:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Por favor, insira um e-mail válido.")

else:
    # --- MENU LATERAL ---
    st.sidebar.markdown("# 🌱 Painel Vegano")
    st.sidebar.write(f"Conectado como: \n**{st.session_state.usuario}**")
    st.sidebar.divider()
    pagina = st.sidebar.radio("Navegação:", ["👤 Meu Perfil (TMB)", "🍽️ Diário de Refeições", "🔍 Banco de Alimentos"])
    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.carrinho = []
        st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA: MEU PERFIL (TOTALMENTE AJUSTADA) ---
    if pagina == "👤 Meu Perfil (TMB)":
        st.header("👤 Perfil & Gasto Energético")
        col_corporal, col_metas = st.columns(2)
        
        with col_corporal:
            st.subheader("1. Dados Corporais (Cálculo TMB)")
            peso = st.number_input("Peso Atual (kg):", value=70.0, step=0.1)
            altura = st.number_input("Altura (cm):", value=170.0, step=1.0)
            idade = st.number_input("Idade (anos):", value=25, step=1)
            sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
            
            # Cálculo TMB (Mifflin-St Jeor)
            if sexo == "Masculino":
                tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
            else:
                tmb_base = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
            
            st.session_state.perfil["tmb"] = tmb_base
            st.info(f"Sua TMB Base: **{tmb_base:.0f} kcal**")
            st.write("*(Gasto do corpo em repouso absoluto)*")

            st.divider()
            st.subheader("2. Nível de Atividade (GET)")
            
            # Opções EXATAS da imagem fornecida
            fatores_atividade = {
                "Sedentário": 1.2,
                "Levemente ativo": 1.375,
                "Moderadamente ativo": 1.55,
                "Muito ativo": 1.725,
                "Extremamente ativo": 1.9
            }
            
            # Seletor com as opções fidelizadas
            nivel_selecionado = st.selectbox(
                "Selecione seu nível de atividade:",
                options=list(fatores_atividade.keys()),
                index=0 # Padrão Sedentário
            )
            
            # Cálculo do Gasto Energético Total (GET)
            gasto_total = tmb_base * fatores_atividade[nivel_selecionado]
            st.session_state.perfil["get"] = gasto_total
            
            st.success(f"Seu Gasto Diário Estimado (GET): **{gasto_total:.0f} kcal**")
            st.write(f"*(Cálculo com multiplicador de {fatores_atividade[nivel_selecionado]})*")

        with col_metas:
            st.subheader("3. Defina Suas Metas Manuais")
            st.write("*(O app não dará sugestões, defina seu próprio plano)*")
            
            # Campos de input manuais para as metas, sem sugestão automática
            st.session_state.perfil["meta_kcal"] = st.number_input(
                "Sua Meta Diária de Calorias (kcal):", 
                value=int(st.session_state.perfil["meta_kcal"]), # Mantém o que o usuário definiu
                step=50
            )
            
            st.session_state.perfil["meta_prot"] = st.number_input(
                "Sua Meta Diária de Proteínas (g):", 
                value=int(st.session_state.perfil["meta_prot"]), # Mantém o que o usuário definiu
                step=1
            )
            
            # Validação simples
            if st.session_state.perfil["meta_kcal"] > 0 and peso > 0:
                diferenca = st.session_state.perfil["meta_kcal"] - gasto_total
                estratégia = "Manutenção" if abs(diferenca) < 50 else ("Déficit" if diferenca < 0 else "Superávit")
                prot_kg = st.session_state.perfil["meta_prot"] / peso
                
                st.markdown(f"""
                > **Resumo do Plano Definido:**
                > - **Estratégia:** {estratégia} ({abs(diferenca):.0f} kcal em relação ao GET)
                > - **Proteína/kg:** {prot_kg:.1f} g/kg de peso corporal.
                """)
            else:
                st.warning("Defina suas metas acima para que possamos comparar no diário.")

    # --- PÁGINA: DIÁRIO (MONTAR REFEIÇÃO) ---
    elif pagina == "🍽️ Diário de Refeições":
        st.header("🍽️ Diário de Refeições")
        tipo_ref = st.selectbox("Refeição atual:", ["Café da Manhã", "Lanche", "Almoço", "Jantar", "Ceia"])
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.subheader("➕ Adicionar Alimento")
            ali_sel = st.selectbox("Escolha o alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (g):", min_value=1, value=100, step=10)
            
            if st.button("Adicionar ao Prato"):
                dados = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                f = qtd / 100
                st.session_state.carrinho.append({
                    "Refeição": tipo_ref,
                    "Alimento": ali_sel,
                    "Gramas": int(qtd),
                    "Kcal": round(dados['CALORIAS'] * f, 1),
                    "Prot": round(dados['PROTEÍNAS'] * f, 1)
                })
                st.rerun()

        with col2:
            st.subheader("🛒 Resumo do Dia")
            if st.session_state.carrinho:
                try:
                    df_c = pd.DataFrame(st.session_state.carrinho)
                    st.dataframe(df_c, use_container_width=True, hide_index=True)
                    
                    # Verificação de segurança para colunas
                    if 'Kcal' in df_c.columns and 'Prot' in df_c.columns:
                        total_k = df_c['Kcal'].sum()
                        total_p = df_c['Prot'].sum()
                        
                        st.divider()
                        m1, m2 = st.columns(2)
                        
                        meta_k = st.session_state.perfil['meta_kcal']
                        meta_p = st.session_state.perfil['meta_prot']
                        
                        # Exibe o progresso apenas se houver meta definida
                        if meta_k > 0:
                            m1.metric("Kcal Totais Consumidas", f"{total_k:.0f} kcal", f"{meta_k - total_k:.0f} restantes")
                        else:
                            m1.metric("Kcal Totais Consumidas", f"{total_k:.0f} kcal")
                            
                        if meta_p > 0:
                            m2.metric("Proteína Total Consumida", f"{total_p:.1f} g", f"{meta_p - total_p:.1f} g restantes")
                        else:
                            m2.metric("Proteína Total Consumida", f"{total_p:.1f} g")
                            
                except:
                    st.session_state.carrinho = []
                    st.rerun()
                
                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("O prato está vazio. Comece adicionando um alimento!")

    # --- PÁGINA: BANCO DE ALIMENTOS ---
    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Banco de Alimentos")
        busca = st.text_input("Pesquisar por nome do alimento:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
