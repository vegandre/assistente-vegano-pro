import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL (TEMA VEGANO) ---
st.set_page_config(page_title="Assistente Vegano Pro", page_icon="🌱", layout="wide")

# CSS para forçar cores mais vivas e verdes
st.markdown("""
    <style>
    .main { background-color: #f0f7f0; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 10px; }
    .stTextInput>div>div>input { border-color: #2e7d32; }
    h1, h2, h3 { color: #1b5e20; }
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

# --- LÓGICA DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🌱 Bem-vindo ao Assistente Vegano")
    email = st.text_input("Digite seu e-mail para acessar:")
    if st.button("Acessar meu Painel"):
        if "@" in email: # Validação simples de e-mail
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
        else:
            st.error("Por favor, insira um e-mail válido.")

else:
    # --- MENU LATERAL ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2324/2324483.png", width=100)
    st.sidebar.write(f"Logado como: **{st.session_state.usuario}**")
    pagina = st.sidebar.radio("Navegação", ["Diário / Carrinho", "Histórico (Calendário)", "Banco de Alimentos"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA: DIÁRIO / CARRINHO ---
    if pagina == "Diário / Carrinho":
        st.header("🍽️ Montar Refeição do Dia")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Adicionar Alimento")
            ali_sel = st.selectbox("Escolha o alimento:", df_ali.iloc[:, 0].unique())
            qtd = st.number_input("Quantidade (g):", min_value=1, value=100)
            
            if st.button("➕ Adicionar ao Carrinho"):
                row = df_ali[df_ali.iloc[:, 0] == ali_sel].iloc[0]
                fator = qtd / 100
                item = {
                    "Alimento": ali_sel,
                    "Qtd": qtd,
                    "Kcal": round(row['CALORIAS'] * fator, 2),
                    "Prot": round(row['PROTEÍNAS'] * fator, 2)
                }
                st.session_state.carrinho.append(item)
                st.success(f"{ali_sel} adicionado!")

        with col2:
            st.subheader("🛒 Itens Selecionados")
            if st.session_state.carrinho:
                df_carrinho = pd.DataFrame(st.session_state.carrinho)
                st.table(df_carrinho)
                
                total_kcal = df_carrinho['Kcal'].sum()
                total_prot = df_carrinho['Prot'].sum()
                
                st.metric("Total Calorias", f"{total_kcal:.2f} kcal")
                st.metric("Total Proteínas", f"{total_prot:.2f} g")
                
                if st.button("💾 Salvar Refeição no Histórico"):
                    st.warning("Para salvar permanentemente, precisamos configurar a API do Google Sheets (próximo passo!).")
                    # Aqui simularemos o save
                    st.session_state.carrinho = []
                    st.success("Refeição salva no seu histórico local!")
            else:
                st.info("Seu carrinho está vazio.")

    # --- PÁGINA: HISTÓRICO (CALENDÁRIO) ---
    elif pagina == "Histórico (Calendário)":
        st.header("📅 Consultar Histórico")
        data_sel = st.date_input("Selecione o dia para revisar:", datetime.now())
        st.info(f"Mostrando dados de {data_sel} para {st.session_state.usuario}")
        # Futuramente: df_hist[df_hist['Data'] == data_sel]
        st.write("Em breve: Integração completa com a aba 'historico' da planilha.")

    # --- PÁGINA: BANCO DE ALIMENTOS ---
    elif pagina == "Banco de Alimentos":
        st.header("🔍 Consulta de Alimentos")
        st.dataframe(df_ali, use_container_width=True, hide_index=True)
