import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    h1, h2, h3 { color: #1B5E20 !important; font-weight: 700 !important;}
    label { color: #1B5E20 !important; font-weight: 600 !important;}
    .stApp { background-color: #FFFFFF; }
    .stButton>button { 
        background-color: #388E3C; 
        color: white; 
        border-radius: 8px; 
        width: 100%; 
        font-weight: bold;
    }
    div[data-testid="stMarkdownContainer"] > blockquote { 
        border-left: 5px solid #2e7d32; 
        background-color: #f1f8e9; 
        padding: 15px; 
        border-radius: 5px; 
        color: #333333;
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
        cols_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'metas' not in st.session_state:
    st.session_state.metas = {"kcal": 3000, "prot": 150, "carb": 350, "gord": 80, "fibra": 35, "get": 0}

# --- 4. NAVEGAÇÃO ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail:")
    if st.button("Acessar"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    with st.sidebar:
        st.title("🌱 Menu")
        st.write(f"Usuário: **{st.session_state.usuario}**")
        pagina = st.radio("Ir para:", ["👤 Perfil & Metas", "🍽️ Diário Alimentar", "🔍 Banco de Dados"])
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    df_ali = carregar_alimentos()

    if pagina == "👤 Perfil & Metas":
        st.header("👤 Perfil & Metas")
        c1, c2 = st.columns(2)
        with c1:
            peso = st.number_input("Peso (kg)", value=68.0)
            altura = st.number_input("Altura (cm)", value=154.0)
            idade = st.number_input("Idade", value=20)
            sexo = st.selectbox("Sexo", ["MASCULINO", "FEMININO"])
            tmb = (88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)) if sexo == "MASCULINO" else (447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade))
            st.info(f"TMB: {tmb:.0f} kcal")
        with c2:
            st.session_state.metas["kcal"] = st.number_input("Meta Kcal", value=int(st.session_state.metas["kcal"]))
            st.session_state.metas["prot"] = st.number_input("Meta Prot (g)", value=int(st.session_state.metas["prot"]))
            st.session_state.metas["carb"] = st.number_input("Meta Carb (g)", value=int(st.session_state.metas["carb"]))
            st.session_state.metas["gord"] = st.number_input("Meta Gord (g)", value=int(st.session_state.metas["gord"]))
            st.session_state.metas["fibra"] = st.number_input("Meta Fibra (g)", value=int(st.session_state.metas["fibra"]))

    elif pagina == "🍽️ Diário Alimentar":
        st.header("🍽️ Diário de Refeições")
        col_add, col_resumo = st.columns([1, 1.8])
        
        with col_add:
            st.subheader("➕ Novo Alimento")
            ref = st.selectbox("Refeição:", ["Café da Manhã", "Almoço", "Lanche", "Jantar", "Ceia"])
            if not df_ali.empty:
                ali = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
                qtd = st.number_input("Peso (g):", min_value=1, value=100)
                if st.button("Lançar no Diário"):
                    row = df_ali[df_ali.iloc[:, 0] == ali].iloc[0]
                    f = qtd / 100
                    st.session_state.carrinho.append({
                        "Refeição": ref, "Alimento": ali, "Peso": int(qtd),
                        "Kcal": row['CALORIAS'] * f, "Prot": row['PROTEÍNAS'] * f,
                        "Carb": row['CARBOIDRATOS'] * f, "Gord": row['GORDURAS'] * f, "Fibra": row['FIBRA'] * f
                    })
                    st.rerun()

        with col_resumo:
            st.subheader("📊 Resumo do Dia")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                st.dataframe(df_c[["Refeição", "Alimento", "Peso", "Kcal", "Prot"]], use_container_width=True, hide_index=True)
                
                tot = df_c.sum(numeric_only=True)
                st.divider()
                
                g1, g2 = st.columns([1, 1.5])
                with g1:
                    cp, cc, cg = tot['Prot']*4, tot['Carb']*4, tot['Gord']*9
                    if (cp+cc+cg) > 0:
                        fig_p = px.pie(values=[cp, cc, cg], names=["Proteínas", "Carbos", "Gorduras"], title="% Calórica", color_discrete_sequence=px.colors.qualitative.Prism)
                        fig_p.update_layout(showlegend=False)
                        fig_p.update_traces(textinfo='percent+label')
                        st.plotly_chart(fig_p, use_container_width=True)
                
                with g2:
                    m = st.session_state.metas
                    labels = ["Kcal", "Prot", "Carb", "Gord", "Fibra"]
                    cons = [tot['Kcal'], tot['Prot'], tot['Carb'], tot['Gord'], tot['Fibra']]
                    metas_v = [m['kcal'], m['prot'], m['carb'], m['gord'], m['fibra']]
                    rest = [max(0, mv - cv) for mv, cv in zip(metas_v, cons)]
                    
                    fig_b = go.Figure()
                    fig_b.add_trace(go.Bar(y=labels, x=cons, name='Consumido', orientation='h', marker_color='#388E3C'))
                    fig_b.add_trace(go.Bar(y=labels, x=rest, name='Restante', orientation='h', marker_color='#E0E0E0'))
                    fig_b.update_layout(barmode='stack', title="Metas vs Consumo", height=300, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig_b, use_container_width=True)

                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Lance um alimento para ver as estatísticas.")

    elif pagina == "🔍 Banco de Dados":
        st.header("🔍 Banco de Dados")
        st.dataframe(df_ali, use_container_width=True, hide_index=True)
