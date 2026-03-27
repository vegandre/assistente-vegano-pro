import streamlit as st
import pandas as pd
import plotly.express as px  # Importamos para os gráficos de pizza
import plotly.graph_objects as go # Importamos para os gráficos de barras complexos

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    page_title="Assistente Vegano Pro", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS PERSONALIZADO (Ajustado para gráficos) ---
st.markdown("""
    <style>
    /* Cores Globais */
    h1, h2, h3 { color: #1B5E20 !important; font-weight: 700 !important;}
    label { color: #1B5E20 !important; font-weight: 600 !important; font-size: 1.1rem !important;}
    .stApp { background-color: #FFFFFF; }
    
    /* Botões */
    .stButton>button { 
        background-color: #388E3C; 
        color: white; 
        border-radius: 8px; 
        width: 100%; 
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover { background-color: #2E7D32; }

    /* Estilo de caixas de texto de métrica */
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
        # Tratamento numérico rigoroso
        cols_num = ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS', 'FIBRA']
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

if 'logado' not in st.session_state: st.session_state.logado = False
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
# Metas padrão iniciais para evitar erros de primeiro acesso
if 'metas' not in st.session_state:
    st.session_state.metas = {"kcal": 3000, "prot": 150, "carb": 350, "gord": 80, "fibra": 35, "get": 0}

# --- 4. LÓGICA DE NAVEGAÇÃO ---
if not st.session_state.logado:
    st.title("🌱 Assistente Nutricional Vegano")
    email = st.text_input("E-mail para login:")
    if st.button("Acessar Painel"):
        if "@" in email:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.rerun()
else:
    with st.sidebar:
        st.title("🌱 Menu Vegano")
        st.write(f"Conectado: **{st.session_state.usuario}**")
        st.divider()
        pagina = st.radio("Ir para:", ["👤 Perfil & Metas", "🍽️ Diário Alimentar", "🔍 Banco de Dados"])
        st.divider()
        if st.button("Sair"):
            st.session_state.logado = False
            st.session_state.carrinho = [] # Limpa o diário ao sair
            st.rerun()

    df_ali = carregar_alimentos()

    # --- PÁGINA PERFIL ---
    if pagina == "👤 Perfil & Metas":
        st.header("👤 Perfil & Metabolismo")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Seus Dados Corporais")
            peso = st.number_input("Peso (kg)", value=68.0, step=0.1)
            altura = st.number_input("Altura (cm)", value=154.0, step=1.0)
            idade = st.number_input("Idade (anos)", value=20)
            sexo = st.selectbox("Sexo Biológico", ["MASCULINO", "FEMININO"])
            
            # Fórmula Harris-Benedict Revisada (Roza & Shizgal, 1984)
            if sexo == "MASCULINO":
                tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
            else:
                tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)
            
            st.info(f"Sua TMB Base: **{tmb:.0f} kcal**")
            st.divider()
            
            st.subheader("2. Nível de Atividade Diária")
            fatores = {"SEDENTÁRIO": 1.2, "LEVEMENTE ATIVO": 1.38, "MODERADAMENTE ATIVO": 1.55, "MUITO ATIVO": 1.73, "EXTREMAMENTE ATIVO": 1.9}
            nivel = st.selectbox("Selecione sua rotina:", list(fatores.keys()))
            st.session_state.metas["get"] = tmb * fatores[nivel]
            st.success(f"Gasto Total Diário (GET): **{st.session_state.metas['get']:.0f} kcal**")

        with col2:
            st.subheader("3. Definição de Metas (Manual)")
            st.write("*(Valores que você quer atingir por dia)*")
            st.session_state.metas["kcal"] = st.number_input("Meta Calorias Diárias", value=int(st.session_state.metas["kcal"]))
            st.session_state.metas["prot"] = st.number_input("Meta Proteínas (g)", value=int(st.session_state.metas["prot"]))
            st.session_state.metas["carb"] = st.number_input("Meta Carboidratos (g)", value=int(st.session_state.metas["carb"]))
            st.session_state.metas["gord"] = st.number_input("Meta Gorduras (g)", value=int(st.session_state.metas["gord"]))
            st.session_state.metas["fibra"] = st.number_input("Meta Fibras (g)", value=int(st.session_state.metas["fibra"]))
            
            # Resumo visual simples
            dif_cal = st.session_state.metas["kcal"] - st.session_state.metas["get"]
            balanco = "Superávit (Ganhar peso)" if dif_cal > 0 else "Déficit (Perder peso)"
            
            st.markdown(f"""
            > **Balanço Definido:**
            > - **Diferença para o Gasto:** {dif_cal:+.0f} kcal
            > - **Estado:** {balanco}
            > - **Relação Prot/Peso:** {st.session_state.metas['prot']/peso:.2f} g/kg
            """)

    # --- PÁGINA DIÁRIO (NOVA LÓGICA DE GRÁFICOS) ---
    elif pagina == "🍽️ Diário Alimentar":
        st.header("🍽️ Diário de Refeições Diárias")
        
        col_add, col_resumo = st.columns([1, 1.8])
        
        with col_add:
            st.subheader("➕ Novo Alimento")
            ref_tipo = st.selectbox("Refeição:", ["Café da Manhã", "Almoço", "Lanche 1", "Lanche 2", "Jantar", "Ceia"])
            
            if not df_ali.empty:
                # Sistema de busca aprimorado no selectbox
                ali_txt = st.selectbox("Selecione o Alimento:", df_ali.iloc[:, 0].unique())
                qtd_g = st.number_input("Peso (g):", min_value=1, value=100, step=10)
                
                if st.button("Lançar no Diário"):
                    # Busca a linha do alimento e faz o cálculo proporcional
                    linha_ali = df_ali[df_ali.iloc[:, 0] == ali_txt].iloc[0]
                    f = qtd_g / 100
                    
                    st.session_state.carrinho.append({
                        "Refeição": ref_tipo,
                        "Alimento": ali_txt,
                        "Grams": int(qtd_g),
                        "Kcal": round(linha_ali['CALORIAS'] * f, 1),
                        "Prot": round(linha_ali['PROTEÍNAS'] * f, 1),
                        "Carb": round(linha_ali['CARBOIDRATOS'] * f, 1),
                        "Gord": round(linha_ali['GORDURAS'] * f, 1),
                        "Fibra": round(linha_ali['FIBRA'] * f, 1)
                    })
                    st.rerun()

        with col_resumo:
            st.subheader("📊 Totais de Hoje")
            if st.session_state.carrinho:
                df_c = pd.DataFrame(st.session_state.carrinho)
                # Tabela organizada
                st.dataframe(df_c[["Refeição", "Alimento", "Grams", "Kcal", "Prot"]], use_container_width=True, hide_index=True)
                
                totais = df_c.sum(numeric_only=True)
                st.divider()
                
                # --- ÁREA DE GRÁFICOS ---
                graf_pizza, graf_barras = st.columns([1.2, 2])
                
                # 1. Gráfico de Pizza: Distribuição Calórica dos Macros
                with graf_pizza:
                    # Cálculo simples das calorias de cada macro (carb=4, prot=4, gord=9)
                    c_prot = totais['Prot'] * 4
                    c_carb = totais['Carb'] * 4
                    c_gord = totais['Gord'] * 9
                    total_c = c_prot + c_carb + c_gord
                    
                    if total_c > 0:
                        data_pizza = {
                            "Macro": ["Proteínas", "Carbos", "Gorduras"],
                            "Calorias": [c_prot, c_carb, c_gord]
                        }
                        fig_pizza = px.pie(
                            data_pizza, values='Calorias', names='Macro',
                            title="Distribuição em % (por Kcal)",
                            color_discrete_sequence=px.colors.qualitative.Prism # Cores mais vivas
                        )
                        # Remove a legenda para ganhar espaço
                        fig_pizza.update_layout(showlegend=False)
                        # Mostra as labels direto na pizza
                        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pizza, use_container_width=True)
                    else:
                        st.write("*(Sem macros para gráfico de pizza)*")

                # 2. Gráfico de Barras: Consumo vs Metas
                with graf_barras:
                    m = st.session_state.metas
                    t = totais
                    
                    # Dados para o gráfico (nomes, consumido, meta)
                    macros_nomes = ["Calorias (kcal)", "Prot (g)", "Carb (g)", "Gord (g)", "Fibra (g)"]
                    consumido = [t['Kcal'], t['Prot'], t['Carb'], t['Gord'], t['Fibra']]
                    metas_v = [m['kcal'], m['prot'], m['carb'], m['gord'], m['fibra']]
                    
                    # Criação do gráfico de barras "empilhadas" (Consumed + Remaining = Meta)
                    fig_bar = go.Figure()
                    
                    # Barra 1: Consumido
                    fig_bar.add_trace(go.Bar(
                        y=macros_nomes, x=consumido,
                        name='Consumido', orientation='h',
                        marker=dict(color='#388E3C') # Verde forte do app
                    ))
                    
                    # Cálculo do que falta (Remaining)
                    faltando = [max(0, mv - cv) for mv, cv in zip(metas_v, consumido)]
                    
                    # Barra 2: Faltando (em cinza claro)
                    fig_bar.add_trace(go.Bar(
                        y=macros_nomes, x=faltando,
                        name='Faltando', orientation='h',
                        marker=dict(color='#E0E0E0') # Cinza claro
                    ))
                    
                    # Configuração final do layout (empilhado)
                    fig_bar.update_layout(
                        barmode='stack', # Empilha as barras
                        title="Consumo Diário vs Metas",
                        xaxis_title="Quantidade",
                        margin=dict(l=10, r=10, t=40, b=10), # Ganhar espaço
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # Legenda no topo
                    )
                    
                    st.plotly_chart(fig_bar, use_container_width=True)

                if st.button("🗑️ Limpar Diário"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("O prato está vazio. Adicione um alimento para ver os totais e gráficos.")

    # --- PÁGINA BANCO (Ajustada para novos nomes de coluna) ---
    elif pagina == "🔍 Banco de Dados":
        st.header("🔍 Banco de Dados Nutricionais Veganos")
        st.write("*(Dados puxados da sua Planilha do Google)*")
        busca = st.text_input("Filtrar por nome do alimento:")
        df_f = df_ali.copy()
        if busca:
            df_f = df_f[df_f.iloc[:, 0].str.contains(busca, case=False, na=False)]
        
        # Mostra apenas as colunas principais na busca
        cols_viz = df_f.columns[0:2].tolist() + ['CALORIAS', 'PROTEÍNAS', 'CARBOIDRATOS', 'GORDURAS']
        st.dataframe(df_f[cols_viz], use_container_width=True, hide_index=True)
