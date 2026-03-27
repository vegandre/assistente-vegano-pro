import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    page_title="Diário Vegano Pro | Neon Edition", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS PERSONALIZADO (NOVO ESTILO ESTÉTICO NEON PRO) ---
st.markdown("""
    <style>
    /* 1. FUNDO GLOBAL E SIDEBARS (DEGRADÊ NEON ROXO-AZUL) */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    .stApp { 
        background-color: #0E021A; /* Fundo escuro base */
        background-image: linear_gradient(135deg, #240b36 0%, #c31432 100%); /* Degradê Neon */
        font-family: 'Roboto', sans-serif !important;
        color: #E0E0E0 !important; /* Texto claro */
    }

    [data-testid="stSidebar"] { 
        background: rgba(14, 2, 26, 0.8) !important; /* Fundo escuro translúcido */
        border-right: 1px solid rgba(136, 14, 186, 0.3); /* Borda roxa sutil */
    }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; }

    /* 2. TÍTULOS E LABELS COM BRILHO NEON */
    h1, h2, h3, label { 
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        text_shadow: 0 0 10px rgba(0, 255, 255, 0.5); /* Brilho Ciano Neon */
    }
    label { font-weight: 400 !important; color: #FFFFFF !important;}

    /* 3. CARTÕES DE CONTEÚDO (FLOAT-NEON-CARD) */
    div[data-testid="stBlock"] {
        background: rgba(14, 2, 26, 0.8) !important;
        border-radius: 15px;
        padding: 20px !important;
        box-shadow: 0 0 25px rgba(136, 14, 186, 0.3), inset 0 0 10px rgba(136, 14, 186, 0.1); /* Brilho e Sombra Roxo Neon */
        margin-bottom: 15px;
    }

    /* 4. BOTÕES NEON */
    .stButton>button { 
        background-color: #388E3C; /* Verde padrão */
        background: linear_gradient(135deg, #1d976c 0%, #93f9b9 100%); /* Degradê Neon */
        color: #FFFFFF !important; 
        border-radius: 10px; 
        width: 100%; 
        font-weight: 700;
        border: none;
        padding: 12px;
        box-shadow: 0 0 15px rgba(147, 249, 185, 0.3); /* Brilho Neon */
        text_transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover { 
        background-image: linear_gradient(135deg, #1d976c 20%, #93f9b9 120%);
        box-shadow: 0 0 25px rgba(147, 249, 185, 0.5);
    }

    /* 5. RESUMO DE TEXTO E TABELAS COM BRILHO */
    div[data-testid="stMarkdownContainer"] > blockquote { 
        border-left: 5px solid #00E5FF; /* Ciano Neon */
        background-color: rgba(0, 229, 255, 0.05); /* Fundo translúcido */
        padding: 15px; 
        border-radius: 8px; 
        color: #E0E0E0;
        text_shadow: 0 0 5px rgba(0, 229, 255, 0.3);
    }
    
    /* Tabelas */
    .stDataFrame, div[data-testid="stDataFrame"] > div > div > div > table {
        background-color: rgba(14, 2, 26, 0.5) !important;
        border-color: rgba(136, 14, 186, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS E SESSÃO (Ajustado para gráficos) ---
ID_PLANILHA = "1bifCd5RseTG-MYvJa3aJwqk0Mdk9-31tfH4BbO2un0w"
GID_DADOS = "1577491175"
URL_ALIMENTOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid={GID_DADOS}"

@st.cache_data
def carregar_alimentos():
    try:
        df = pd.read_csv(URL_ALIMENTOS, header=7)
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = df.columns.str.strip().str.upper()
        # Tratamento numérico vigoroso
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
    st.title("🌱 Painel Nutricional Vegano")
    email = st.text_input("E-mail:")
    if st.button("Acessar Painel"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    with st.sidebar:
        st.title("🌱 Menu Vegano")
        st.write(f"Usuário: **{st.session_state.usuario}**")
        st.divider()
        pagina = st.radio("Navegação:", ["👤 Perfil & Metas", "🍽️ Diário Alimentar", "🔍 Banco de Dados"])
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA PERFIL ---
    if pagina == "👤 Perfil & Metas":
        st.header("👤 Perfil & Metas Diárias")
        c1, c2 = st.columns(2)
        with c1:
            peso = st.number_input("Peso (kg)", value=68.0, step=0.1)
            altura = st.number_input("Altura (cm)", value=154.0, step=1.0)
            idade = st.number_input("Idade", value=20)
            sexo = st.selectbox("Sexo", ["MASCULINO", "FEMININO"])
            tmb = (88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)) if sexo == "MASCULINO" else (447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade))
            st.info(f"TMB Base: {tmb:.0f} kcal")
        with c2:
            st.session_state.metas["kcal"] = st.number_input("Meta Calorias", value=int(st.session_state.metas["kcal"]))
            st.session_state.metas["prot"] = st.number_input("Meta Prot (g)", value=int(st.session_state.metas["prot"]))
            st.session_state.metas["carb"] = st.number_input("Meta Carb (g)", value=int(st.session_state.metas["carb"]))
            st.session_state.metas["gord"] = st.number_input("Meta Gord (g)", value=int(st.session_state.metas["gord"]))
            st.session_state.metas["fibra"] = st.number_input("Meta Fibra (g)", value=int(st.session_state.metas["fibra"]))

    # --- PÁGINA DIÁRIO (NOVO ESTILO GRÁFICO NEON) ---
    elif pagina == "🍽️ Diário Alimentar":
        st.header("🍽️ Diário de Refeições Diárias")
        col_add, col_resumo = st.columns([1, 1.8])
        
        # Coluna de Adicionar Alimento
        with col_add:
            st.subheader("➕ Novo Lançamento")
            ref = st.selectbox("Refeição:", ["Café da Manhã", "Almoço", "Lanche", "Jantar", "Ceia"])
            if not df_ali.empty:
                ali = st.selectbox("Alimento:", df_ali.iloc[:, 0].unique())
                qtd = st.number_input("Peso (g):", min_value=1, value=100)
                if st.button("Adicionar ao Dia"):
                    row = df_ali[df_ali.iloc[:, 0] == ali].iloc[0]
                    f = qtd / 100
                    st.session_state.carrinho.append({
                        "Refeição": ref, "Alimento": ali, "Peso": int(qtd),
                        "Kcal": row['CALORIAS'] * f, "Prot": row['PROTEÍNAS'] * f,
                        "Carb": row['CARBOIDRATOS'] * f, "Gord": row['GORDURAS'] * f, "Fibra": row['FIBRA'] * f
                    })
                    st.rerun()

        # Coluna de Resumo (Tabela + Gráficos Neon)
        with col_resumo:
            st.subheader("📊 Totais de Hoje")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                # Tabela organizada
                st.dataframe(df_c[["Refeição", "Alimento", "Peso", "Kcal", "Prot"]], use_container_width=True, hide_index=True)
                
                # Totais numéricos
                t = df_c.sum(numeric_only=True)
                st.divider()
                
                # --- ÁREA DE GRÁFICOS NEON ---
                # Aumentando o espaço para o gráfico de barras
                g1, g2 = st.columns([1.1, 2.2])
                
                # 1. Gráfico de Pizza (Donut Neon) - Similar ao modelo
                with g1:
                    cp, cc, cg = t['Prot']*4, t['Carb']*4, t['Gord']*9
                    if (cp+cc+cg) > 0:
                        # Dados
                        data_donut = {
                            "Macro": ["Proteínas", "Carbos", "Gorduras"],
                            "Calorias": [cp, cc, cg]
                        }
                        # Paleta de cores baseada no modelo Neon (Azul, Turquesa, Roxo)
                        neon_colors = ['#00BFFF', '#00FFCC', '#8A2BE2']
                        
                        fig_p = px.pie(
                            data_donut, values='Calorias', names='Macro', 
                            title="% Calórica (Neon Donut)",
                            hole=0.6, # Transforma em gráfico de rosca (Donut)
                            color_discrete_sequence=neon_colors
                        )
                        # Ajustes Estéticos: transparente e sem legenda
                        fig_p.update_layout(
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente para degradê aparecer
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#FFFFFF'), # Fonte branca
                            title=dict(font=dict(color='#FFFFFF', size=16), x=0.2)
                        )
                        fig_p.update_traces(
                            textposition='inside', 
                            textinfo='percent+label',
                            hoverinfo='label+percent+value',
                            marker=dict(line=dict(color='#1A1A1A', width=2)) # Borda fina
                        )
                        st.plotly_chart(fig_p, use_container_width=True)
                    else:
                        st.write("*(Lance alimentos para ver o gráfico)*")

                # 2. Gráfico de Barras Horizontal (Consumo vs Metas Neon)
                with g2:
                    m = st.session_state.metas
                    labels = ["Kcal", "Prot", "Carb", "Gord", "Fibra"]
                    cons = [t['Kcal'], t['Prot'], t['Carb'], t['Gord'], t['Fibra']]
                    metas_v = [m['kcal'], m['prot'], m['carb'], m['gord'], m['fibra']]
                    # Cálculo do restante
                    rest = [max(0, mv - cv) for mv, cv in zip(metas_v, cons)]
                    
                    fig_b = go.Figure()
                    
                    # Barra 1: Consumido (Verde-limão brilhante)
                    fig_b.add_trace(go.Bar(
                        y=labels, x=cons, 
                        name='Consumido', orientation='h', 
                        marker_color='#CCFF00', # Verde-limão neon
                        # Brilho sutil na barra
                        marker=dict(line=dict(color='#CCFF00', width=1))
                    ))
                    
                    # Barra 2: Restante (Cinza escuro, como no modelo)
                    fig_b.add_trace(go.Bar(
                        y=labels, x=rest, 
                        name='Restante', orientation='h', 
                        marker_color='#2A2A2A' # Cinza muito escuro
                    ))
                    
                    # Layout Transparente e Neon
                    fig_b.update_layout(
                        barmode='stack', # Barras empilhadas
                        title="Consumo vs Metas Diárias",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#FFFFFF'),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'), # Grelha translúcida
                        margin=dict(l=0, r=0, t=30, b=10),
                        height=350
                    )
                    st.plotly_chart(fig_b, use_container_width=True)

                if st.button("🗑️ Resetar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("O prato está vazio. Lança um alimento!")

    # --- PÁGINA BANCO ---
    elif pagina == "🔍 Banco de Dados":
        st.header("🔍 Banco de Dados Nutricionais")
        st.dataframe(df_ali, use_container_width=True, hide_index=True)
