import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    page_title="Diário Vegano Pro | Refined Neon", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    .stApp { 
        background-color: #0E021A;
        background-image: linear-gradient(135deg, #240b36 0%, #0E021A 100%);
        font-family: 'Poppins', sans-serif !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] { 
        background: rgba(14, 2, 26, 0.9) !important;
        border-right: 1px solid rgba(136, 14, 186, 0.3);
    }

    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    
    label { 
        font-weight: 600 !important;
        color: #E0E0E0 !important;
    }

    div[data-testid="stBlock"] {
        background: rgba(25, 10, 40, 0.5) !important;
        border-radius: 15px;
        padding: 20px !important;
        border: 1px solid rgba(136, 14, 186, 0.2);
        margin-bottom: 20px;
    }

    .stButton>button { 
        background: linear-gradient(135deg, #1d976c 0%, #93f9b9 100%);
        color: #000000 !important; 
        border-radius: 10px; 
        font-weight: 700 !important;
        border: none;
        text-transform: uppercase;
        letter-spacing: 1px;
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
    st.session_state.metas = {"kcal": 3000, "prot": 150, "carb": 350, "gord": 80, "fibra": 35}

# --- 4. LÓGICA DE NAVEGAÇÃO ---
if not st.session_state.logado:
    st.title("🌱 Login")
    email = st.text_input("E-mail:")
    if st.button("Entrar"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    df_ali = carregar_alimentos()
    pagina = st.sidebar.radio("Navegação", ["👤 Perfil", "🍽️ Diário", "🔍 Banco"])

    if pagina == "👤 Perfil":
        st.header("👤 Metas Diárias")
        m = st.session_state.metas
        m["kcal"] = st.number_input("Kcal", value=int(m["kcal"]))
        m["prot"] = st.number_input("Proteína (g)", value=int(m["prot"]))
        m["carb"] = st.number_input("Carbo (g)", value=int(m["carb"]))
        m["gord"] = st.number_input("Gordura (g)", value=int(m["gord"]))
        m["fibra"] = st.number_input("Fibra (g)", value=int(m["fibra"]))

    elif pagina == "🍽️ Diário":
        st.header("🍽️ Diário Alimentar")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Adicionar")
            refeicao = st.selectbox("Refeição", ["Café da Manhã", "Almoço", "Lanche", "Jantar", "Ceia"])
            ali = st.selectbox("Alimento", df_ali.iloc[:, 0].unique() if not df_ali.empty else ["Nenhum"])
            qtd = st.number_input("Grams", value=100)
            if st.button("LANÇAR"):
                row = df_ali[df_ali.iloc[:, 0] == ali].iloc[0]
                f = qtd / 100
                st.session_state.carrinho.append({
                    "Refeição": refeicao, "Alimento": ali, "Peso": int(qtd),
                    "Kcal": row['CALORIAS'] * f, "Prot": row['PROTEÍNAS'] * f, 
                    "Carb": row['CARBOIDRATOS'] * f, "Gord": row['GORDURAS'] * f, "Fibra": row['FIBRA'] * f
                })
                st.rerun()

        with col2:
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                cols_exis = [c for c in ["Refeição", "Alimento", "Peso", "Kcal", "Prot"] if c in df_c.columns]
                
                st.write("### Itens Lançados")
                st.dataframe(df_c[cols_exis], use_container_width=True, hide_index=True)
                
                tot = df_c.sum(numeric_only=True)
                st.divider()
                
                g1, g2 = st.columns([1, 1.5])
                with g1:
                    fig_p = px.pie(names=["Proteínas", "Carbos", "Gorduras"], values=[tot['Prot']*4, tot['Carb']*4, tot['Gord']*9], hole=0.6, title="<b>% Calórica</b>", color_discrete_sequence=['#00BFFF', '#00FFCC', '#8A2BE2'])
                    fig_p.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins", color="white"), title=dict(font=dict(size=18, color="white")))
                    fig_p.update_traces(textinfo='percent+label', textfont_size=11)
                    st.plotly_chart(fig_p, use_container_width=True)

                with g2:
                    m = st.session_state.metas
                    labs = ["Kcal", "Prot", "Carb", "Gord", "Fibra"]
                    v_cons = [tot['Kcal'], tot['Prot'], tot['Carb'], tot['Gord'], tot['Fibra']]
                    v_meta = [m['kcal'], m['prot'], m['carb'], m['gord'], m['fibra']]
                    v_rest = [max(0, mv - cv) for mv, cv in zip(v_meta, v_cons)]

                    fig_b = go.Figure()
                    fig_b.add_trace(go.Bar(y=labs, x=v_cons, orientation='h', name='Consumido', marker_color='#CCFF00'))
                    fig_b.add_trace(go.Bar(y=labs, x=v_rest, orientation='h', name='Restante', marker_color='#2A2A2A'))
                    fig_b.update_layout(barmode='stack', title="<b>Consumo vs Metas</b>", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins", color="white"), xaxis=dict(tickfont=dict(color='white')), yaxis=dict(tickfont=dict(color='white')), legend=dict(font=dict(color='white'), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=0, r=0, t=50, b=0), height=350)
                    st.plotly_chart(fig_b, use_container_width=True)

                if st.button("LIMPAR TUDO"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("Lance um alimento para ativar os gráficos.")

    elif pagina == "🔍 Banco":
        st.header("🔍 Banco de Alimentos")
        st.write("Consulte aqui as informações nutricionais baseadas na sua planilha.")
        if not df_ali.empty:
            busca = st.text_input("Filtrar alimento:", "")
            df_filt = df_ali[df_ali.iloc[:, 0].str.contains(busca, case=False, na=False)]
            st.dataframe(df_filt, use_container_width=True, hide_index=True)
        else:
            st.error("Não foi possível carregar os dados da planilha.")
