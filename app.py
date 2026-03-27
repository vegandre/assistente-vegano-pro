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

# --- 2. CSS PERSONALIZADO (NOVO ESTILO REFINADO) ---
st.markdown("""
    <style>
    /* 1. FONTES E CORES GLOBAIS (Refinadas para Legibilidade) */
    /* Importando 'Poppins', uma fonte mais limpa e moderna */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .stApp { 
        background-color: #0E021A; /* Fundo escuro base */
        background-image: linear-gradient(135deg, #240b36 0%, #c31432 100%); /* Degradê Neon */
        font-family: 'Poppins', sans-serif !important;
        color: #FFFFFF !important; /* Texto claro */
    }

    [data-testid="stSidebar"] { 
        background: rgba(14, 2, 26, 0.9) !important; /* Fundo escuro translúcido */
        border-right: 1px solid rgba(136, 14, 186, 0.3); /* Borda roxa sutil */
    }
    [data-testid="stSidebar"] * { color: #E0E0E0 !important; font-family: 'Poppins', sans-serif !important; }

    /* 2. TÍTULOS E LABELS COM NEGRIBITO MELHORADO E BRILHO CIANO SUTIL */
    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        text-shadow: 0 0 12px rgba(0, 255, 255, 0.6); /* Brilho Ciano Neon mais visível */
        margin-bottom: 20px !important;
    }
    
    /* Labels dos campos - Semi-bold para legibilidade limpa */
    label { 
        font-weight: 600 !important; /* Semi-bold para destaque sem pesar */
        color: #E0E0E0 !important;
        font-size: 1.05rem !important;
        margin-bottom: 8px !important;
        text-shadow: 0 0 5px rgba(224, 224, 224, 0.3); /* Brilho sutil */
    }

    /* 3. CARTÕES DE CONTEÚDO (FLOAT-NEON-CARD) */
    div[data-testid="stBlock"] {
        background: rgba(14, 2, 26, 0.8) !important;
        border-radius: 18px;
        padding: 25px !important;
        box-shadow: 0 0 30px rgba(136, 14, 186, 0.4), inset 0 0 15px rgba(136, 14, 186, 0.15); /* Brilho Roxo Neon mais forte */
        margin-bottom: 20px;
    }

    /* 4. BOTÕES NEON REFINADOS (Fonte Poppins Bold) */
    .stButton>button { 
        background-color: #388E3C; /* Verde padrão */
        background: linear-gradient(135deg, #1d976c 0%, #93f9b9 100%); /* Degradê Neon */
        color: #FFFFFF !important; 
        border-radius: 12px; 
        width: 100%; 
        font-weight: 700 !important; /* Bold total para botões */
        border: none;
        padding: 14px;
        box-shadow: 0 0 20px rgba(147, 249, 185, 0.4); /* Brilho Neon */
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-family: 'Poppins', sans-serif !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-image: linear-gradient(135deg, #1d976c 20%, #93f9b9 120%);
        box-shadow: 0 0 35px rgba(147, 249, 185, 0.6);
        transform: translateY(-2px); /* Efeito de elevação */
    }

    /* 5. RESUMO DE TEXTO E TABELAS COM BRILHO MELHORADO */
    div[data-testid="stMarkdownContainer"] > blockquote { 
        border-left: 6px solid #00E5FF; /* Ciano Neon mais grosso */
        background-color: rgba(0, 229, 255, 0.08); /* Fundo translúcido */
        padding: 18px; 
        border-radius: 10px; 
        color: #F0F0F0 !important;
        text-shadow: 0 0 6px rgba(0, 229, 255, 0.4);
        font-weight: 400;
    }
    div[data-testid="stMarkdownContainer"] > blockquote p {
        color: #F0F0F0 !important;
    }
    
    /* Tabelas - Mais limpas */
    .stDataFrame, div[data-testid="stDataFrame"] > div > div > div > table {
        background-color: rgba(14, 2, 26, 0.6) !important;
        border-color: rgba(136, 14, 186, 0.3) !important;
        font-size: 0.95rem;
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
    st.title("🌱 Painel Nutricional Vegano")
    email = st.text_input("Seu E-mail:")
    if st.button("Acessar Painel"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    with st.sidebar:
        st.title("🌱 Menu")
        st.write(f"Usuário: **{st.session_state.usuario}**")
        st.divider()
        pagina = st.sidebar.radio("Navegação:", ["👤 Perfil & Metas", "🍽️ Diário Alimentar", "🔍 Banco de Dados"], key="nav_radio")
        if st.sidebar.button("Sair / Logoff"):
            st.session_state.logado = False
            st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA PERFIL ---
    if pagina == "👤 Perfil & Metas":
        st.header("👤 Perfil & Metas Diárias")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("1. Seus Dados Corporais")
            peso = st.number_input("Peso Atual (kg)", value=68.0, step=0.1)
            altura = st.number_input("Altura (cm)", value=154.0, step=1.0)
            idade = st.number_input("Idade (anos)", value=20)
            sexo = st.selectbox("Sexo Biológico", ["MASCULINO", "FEMININO"])
            
            # Cálculo de Roza e Shizgal (Sincronizado)
            if sexo == "MASCULINO":
                tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
            else:
                tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)
            
            st.info(f"TMB Base: {tmb:.0f} kcal")

        with c2:
            st.subheader("2. Definição de Metas")
            st.write("*(Lembre-se de definir as 5 metas diárias)*")
            st.session_state.metas["kcal"] = st.number_input("Meta de Calorias (kcal)", value=int(st.session_state.metas["kcal"]))
            st.session_state.metas["prot"] = st.number_input("Meta de Proteínas (g)", value=int(st.session_state.metas["prot"]))
            st.session_state.metas["carb"] = st.number_input("Meta de Carboidratos (g)", value=int(st.session_state.metas["carb"]))
            st.session_state.metas["gord"] = st.number_input("Meta de Gorduras (g)", value=int(st.session_state.metas["gord"]))
            st.session_state.metas["fibra"] = st.number_input("Meta de Fibras (g)", value=int(st.session_state.metas["fibra"]))

    # --- PÁGINA DIÁRIO (ATUALIZADA PARA O NOVO ESTILO) ---
    elif pagina == "🍽️ Diário Alimentar":
        st.header("🍽️ Diário de Refeições Diárias")
        col_add, col_resumo = st.columns([1, 1.8])
        
        with col_add:
            st.subheader("➕ Novo Lançamento")
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
            st.subheader("📊 Totais de Hoje")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                # Tabela organizada
                st.dataframe(df_c[["Refeição", "Alimento", "Peso", "Kcal", "Prot"]], use_container_width=True, hide_index=True)
                
                tot = df_c.sum(numeric_only=True)
                st.divider()
                
                # --- ÁREA DE GRÁFICOS NEON ---
                g1, g2 = st.columns([1.1, 2.2])
                
                # 1. Gráfico de Pizza (Donut Neon) - Título Limpo
                with g1:
                    cp, cc, cg = tot['Prot']*4, tot['Carb']*4, tot['Gord']*9
                    if (cp+cc+cg) > 0:
                        data_donut = {
                            "Macro": ["Proteínas", "Carbos", "Gorduras"],
                            "Calorias": [cp, cc, cg]
                        }
                        # Paleta de cores baseada no modelo Neon (Azul, Turquesa, Roxo)
                        neon_colors = ['#00BFFF', '#00FFCC', '#8A2BE2']
                        
                        fig_p = px.pie(
                            data_donut, values='Calorias', names='Macro', 
                            title="% Calórica", # TÍTULO LIMPO, SEM O (Neon Don)
                            hole=0.6, 
                            color_discrete_sequence=neon_colors
                        )
                        # Ajustes Estéticos e Fontes Melhoradas
                        fig_p.update_layout(
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Poppins, sans-serif", color='#FFFFFF'), # Fonte Poppins
                            title=dict(font=dict(color='#FFFFFF', size=18, family="Poppins, sans-serif"), x=0.2)
                        )
                        # Fontes internas maiores e em negrito
                        fig_p.update_traces(
                            textposition='inside', 
                            textinfo='percent+label',
                            insidetextfont=dict(color='#0E021A', size=14, family="Poppins, sans-serif", weight="bold"), # Poppins Bold interna
                            hoverinfo='label+percent+value',
                            marker=dict(line=dict(color='#1A1A1A', width=0)) # Removi a borda branca
                        )
                        st.plotly_chart(fig_p, use_container_width=True)
                    else:
                        st.write("*(Lance alimentos para ver o gráfico)*")

                # 2. Gráfico de Barras Horizontal (Consumo vs Metas Neon) - Fontes Melhoradas
                with g2:
                    m = st.session_state.metas
                    labels = ["Kcal", "Prot", "Carb", "Gord", "Fibra"]
                    cons = [tot['Kcal'], tot['Prot'], tot['Carb'], tot['Gord'], tot['Fibra']]
                    metas_v = [m['kcal'], m['prot'], m['carb'], m['gord'], m['fibra']]
                    # Cálculo do restante
                    rest = [max(0, mv - cv) for mv, cv in zip(metas_v, cons)]
                    
                    fig_b = go.Figure()
                    
                    # Barra 1: Consumido (Verde-limão brilhante)
                    fig_b.add_trace(go.Bar(
                        y=labels, x=cons, 
                        name='Consumido', orientation='h', 
                        marker_color='#CCFF00', # Verde-limão neon
                        marker=dict(line=dict(color='#CCFF00', width=1))
                    ))
                    
                    # Barra 2: Restante (Cinza escuro, como no modelo)
                    fig_b.add_trace(go.Bar(
                        y=labels, x=rest, 
                        name='Restante', orientation='h', 
                        marker_color='#2A2A2A' # Cinza muito escuro
                    ))
                    
                    # Layout Transparente e Neon com Fontes Melhoradas
                    fig_b.update_layout(
                        barmode='stack', 
                        title="Consumo vs Metas Diárias",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Poppins, sans-serif", color='#FFFFFF'), # Fonte Poppins
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(family="Poppins, sans-serif", color='#E0E0E0')), # Grelha e ticks Poppins
                        yaxis=dict(tickfont=dict(family="Poppins, sans-serif", color='#E0E0E0', weight="bold")), # Labels de macro Poppins Bold
                        titlefont=dict(family="Poppins, sans-serif", size=18, color='#FFFFFF'),
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
        busca = st.text_input("Filtrar por nome:")
        df_f = df_ali.copy()
        if busca: df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)
