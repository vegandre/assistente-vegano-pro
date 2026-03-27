import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL (FOCO EM LEGIBILIDADE E PROFISSIONALISMO) ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

# CSS para um tema Light limpo, tipografia moderna e contraste alto
st.markdown("""
    <style>
    /* Importando fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* Fundo claro para o app */
    .stApp { background-color: #FFFFFF; }
    
    /* Configuração global de texto para legibilidade máxima */
    html, body, [class*="css"], .stText, .stMarkdown, p, span, label { 
        font-family: 'Roboto', sans-serif !important; 
        color: #333333 !important; /* Texto principal em cinza escuro */
        font-weight: 400;
    }

    /* Estilo para Títulos Principais */
    h1 { color: #1B5E20 !important; font-weight: 700 !important; font-size: 42px !important; margin-bottom: 20px !important;}
    h2, h3 { color: #2E7D32 !important; font-weight: 700 !important; margin-top: 15px !important;}

    /* Menu Lateral Escuro (contraste clássico) */
    [data-testid="stSidebar"] { 
        background-color: #1A1A1A !important; 
        color: #FFFFFF !important; 
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #E0E0E0 !important; 
    }

    /* Botões Profissionais (Sólidos e Robustos) */
    .stButton>button { 
        background-color: #388E3C; 
        color: white !important; 
        border-radius: 6px; 
        font-weight: 700; 
        width: 100%; 
        border: none;
        padding: 12px;
        font-size: 16px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover { background-color: #2E7D32; }

    /* Estilização das Métricas */
    [data-testid="stMetricValue"] { color: #388E3C !important; font-size: 32px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #666666 !important; font-size: 14px !important;}
    
    /* Tabela do Carrinho Limpa */
    .styled-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin: 20px 0; 
        font-size: 16px; 
        background-color: white; 
        border-radius: 8px; 
        overflow: hidden; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .styled-table th { background-color: #E8F5E9; color: #1B5E20; font-weight: 700; padding: 12px; }
    .styled-table td { padding: 10px; border-bottom: 1px solid #EEEEEE; color: #555555; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS (LINKS DA SUA PLANILHA) ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"  # Aba de Alimentos
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

# --- CONTROLE DE SESSÃO E LOGIN ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    st.write("### Por favor, identifique-se para acessar o painel.")
    
    col_l, col_r = st.columns([1, 1])
    with col_l:
        email = st.text_input("Digite seu e-mail:")
        if st.button("Acessar Painel"):
            if "@" in email:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
else:
    # --- MENU LATERAL (ESCURO PARA CONSTRASTE) ---
    st.sidebar.markdown("## 🌱 Painel Vegano")
    st.sidebar.write(f"Conectado como: \n**{st.session_state.usuario}**")
    st.sidebar.divider()
    pagina = st.sidebar.radio("Navegação:", ["🍽️ Montar Refeição", "📅 Histórico", "🔍 Banco de Alimentos"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA: DIÁRIO ---
    if pagina == "🍽️ Montar Refeição":
        st.header("🍽️ Diário de Refeições")
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.subheader("➕ Adicionar Alimento")
            ali_sel = st.selectbox("Escolha o alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (gramas):", min_value=1, value=100, step=10)
            
            if st.button("Adicionar ao Prato"):
                dados = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                fator = qtd / 100
                st.session_state.carrinho.append({
                    "Alimento": ali_sel,
                    "Gramas": int(qtd),
                    "Kcal": round(dados['CALORIAS'] * fator, 1),
                    "Prot(g)": round(dados['PROTEÍNAS'] * fator, 1)
                })
                st.toast(f"✅ {ali_sel} adicionado!")

        with col2:
            st.subheader("🛒 Itens Selecionados")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                
                # Formatação Limpa dos Números
                df_c['Kcal'] = df_c['Kcal'].map('{:.1f}'.format)
                df_c['Prot(g)'] = df_c['Prot(g)'].map('{:.1f}'.format)
                
                st.table(df_c)
                
                # Totais (calculados dos originais)
                df_orig = pd.DataFrame(st.session_state.carrinho)
                t_kcal = df_orig['Kcal'].sum()
                t_prot = df_orig['Prot(g)'].sum()
                
                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Energia Total", f"{t_kcal:.1f} kcal")
                c2.metric("Proteína Total", f"{t_prot:.1f} g")
                
                if st.button("🗑️ Limpar Carrinho"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Adicione um alimento à esquerda para começar!")

    elif pagina == "🔍 Banco de Alimentos":
        st.header("🔍 Banco de Alimentos")
        busca = st.text_input("Pesquisar:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
