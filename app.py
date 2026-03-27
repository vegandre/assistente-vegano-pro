import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL (TEMA VEGANO COLORIDO) ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

# Estilo personalizado para cores verdes e fundo claro
st.markdown("""
    <style>
    .stApp { background-color: #f4f9f4; }
    .stButton>button { background-color: #2e7d32; color: white; border: none; padding: 10px 20px; border-radius: 8px; }
    .stButton>button:hover { background-color: #1b5e20; color: white; }
    h1, h2, h3 { color: #2e7d32; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (LINKS DA SUA PLANILHA) ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"  # Aba de Alimentos
URL_ALIMENTOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"

@st.cache_data
def carregar_alimentos():
    try:
        df = pd.read_csv(URL_ALIMENTOS, header=7)
        # Limpa colunas e linhas vazias
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        # Converte para números reais (corrige o erro de ordenação/texto)
        colunas_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for col in colunas_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- 3. CONTROLE DE SESSÃO E LOGIN ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    st.write("### Bem-vindo! Por favor, identifique-se para continuar.")
    
    with st.container():
        email = st.text_input("Digite seu e-mail:")
        if st.button("Acessar meu Painel"):
            if "@" in email and "." in email:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Por favor, insira um e-mail válido para liberar o acesso.")

else:
    # --- 4. MENU LATERAL ---
    st.sidebar.markdown("# 🌱 Painel Vegano")
    st.sidebar.write(f"Conectado como: \n **{st.session_state.usuario}**")
    st.sidebar.divider()
    
    pagina = st.sidebar.radio("Navegação:", ["🍽️ Montar Refeição", "📅 Histórico Semanal", "🔍 Banco de Alimentos"])
    
    st.sidebar.divider()
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.session_state.carrinho = []
        st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA 1: DIÁRIO / CARRINHO ---
    if pagina == "🍽️ Montar Refeição":
        st.header("🍽️ Diário de Refeições")
        st.write("Adicione os alimentos para calcular o total da sua refeição.")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Adicionar Alimento")
            ali_selecionado = st.selectbox("Selecione o alimento:", df_ali.iloc[:, 0].unique())
            quantidade = st.number_input("Quantidade (gramas):", min_value=1, value=100, step=10)
            
            if st.button("Adicionar ao Prato"):
                dados = df_ali[df_ali.iloc[:, 0] == ali_selecionado].iloc[0]
                fator = quantidade / 100
                novo_item = {
                    "Alimento": ali_selecionado,
                    "Gramas": quantidade,
                    "Kcal": round(dados['CALORIAS'] * fator, 2),
                    "Prot (g)": round(dados['PROTEÍNAS'] * fator, 2),
                    "Carb (g)": round(dados['CARBOIDRATOS'] * fator, 2)
                }
                st.session_state.carrinho.append(novo_item)
                st.toast(f"✅ {ali_selecionado} adicionado!")

        with col2:
            st.subheader("🛒 Itens da Refeição")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                st.table(df_c)
                
                # Totais
                t_kcal = df_c['Kcal'].sum()
                t_prot = df_c['Prot (g)'].sum()
                
                c1, c2 = st.columns(2)
                c1.metric("Total Energia", f"{t_kcal:.2f} kcal")
                c2.metric("Total Proteína", f"{t_prot:.2f} g")
                
                if st.button("🗑️ Limpar Carrinho"):
                    st.session_state.carrinho = []
                    st.rerun()
                
                if st.button("💾 Salvar no Histórico Permanente"):
                    st.info("O salvamento permanente requer integração com a API do Google Sheets (próxima etapa!).")
            else:
                st.info("Seu prato ainda está vazio. Escolha um alimento à esquerda!")

    # --- PÁGINA 2: HISTÓRICO ---
    elif pagina == "📅 Histórico Semanal":
        st.header("📅 Meu Histórico")
        data_consulta = st.date_input("Escolha a data para rever:", datetime.now())
        st.write(f"Mostrando histórico de: **{data_consulta.strftime('%d/%m/%Y')}**")
        st.warning("⚠️ O histórico diário será carregado aqui assim que ativarmos a gravação na planilha.")

    # --- PÁGINA 3: BANCO DE ALIMENTOS ---
    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Consulta de Nutrientes")
        busca = st.text_input("Pesquise por nome (ex: Proteína, Pão, Feijão):")
        
        df_display = df_ali.copy()
        if busca:
            df_display = df_display[df_display.iloc[:, 0].str.contains(busca, case=False, na=False)]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
